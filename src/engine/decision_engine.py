import time
from src.utils.logger import setup_logger
from src.engine.challenge_generator import ChallengeGenerator
from src.engine.challenge_evaluator import ChallengeEvaluator

logger = setup_logger("DecisionEngine")

class DecisionEngine:
    """Orchestrates the entire attendance verification pipeline."""
    
    def __init__(self, db_manager, face_analyzer, liveness_detector, config):
        self.db_manager = db_manager
        self.face_analyzer = face_analyzer
        self.liveness = liveness_detector
        self.config = config
        
        self.evaluator = ChallengeEvaluator()
        self.reset_session()
        
    def reset_session(self):
        """Resets the current verification session state."""
        self.state = "IDLE" # IDLE -> RECOGNIZING -> LIVENESS -> CHALLENGE_1 -> CHALLENGE_2 -> CHALLENGE_3 -> SUCCESS/FAIL
        self.current_user = None
        self.challenges = []
        self.current_challenge_idx = 0
        self.challenge_start_time = 0
        self.evaluator.reset_state()
        self.frames_passed_for_current_task = 0
        self.rejection_reason = ""
        
    def process_frame(self, frame, mp_data):
        """
        Main state machine. Processes a single frame and returns the current state UI data.
        Returns: dict with UI updates (state, instructions, bounding box, status color)
        """
        if self.state == "SUCCESS" or self.state == "FAIL":
            # Wait for reset from UI or auto-reset after 3 seconds
            if not hasattr(self, 'result_time'):
                self.result_time = time.time()
            elif time.time() - self.result_time > 3.0:
                self.reset_session()
                if hasattr(self, 'result_time'):
                    delattr(self, 'result_time')
            return self._build_ui_response()
            
        faces = self.face_analyzer.analyze_frame(frame)
        
        if self.state == "IDLE":
            if len(faces) == 1:
                self.state = "RECOGNIZING"
            elif len(faces) > 1:
                self._fail("Multiple faces detected. Please stand alone.")
            return self._build_ui_response(faces=faces)
            
        elif self.state == "RECOGNIZING":
            if len(faces) != 1:
                self._fail("Lost face or multiple faces detected.")
                return self._build_ui_response()
                
            face = faces[0]
            users = self.db_manager.get_all_users()
            best_match, sim = self.face_analyzer.find_best_match(face.embedding, users, self.config['recognition']['similarity_threshold'])
            
            if best_match:
                self.current_user = best_match
                self.state = "LIVENESS"
                logger.info(f"Recognized user: {best_match['name']} (Sim: {sim:.2f})")
            else:
                self._fail("Face not recognized.")
                
            return self._build_ui_response(faces=faces)
            
        elif self.state == "LIVENESS":
            if len(faces) != 1:
                self._fail("Lost face.")
                return self._build_ui_response()
                
            # Crop face for liveness
            bbox = faces[0].bbox.astype(int)
            # Add margin
            x1, y1, x2, y2 = max(0, bbox[0]-20), max(0, bbox[1]-20), min(frame.shape[1], bbox[2]+20), min(frame.shape[0], bbox[3]+20)
            face_crop = frame[y1:y2, x1:x2]
            
            score = self.liveness.predict(face_crop)
            if score >= self.config['liveness']['threshold']:
                logger.info(f"Liveness passed. Score: {score:.2f}")
                self.state = "CHALLENGE_1"
                self.challenges = ChallengeGenerator.generate_challenges(3)
                self.challenge_start_time = time.time()
                self.evaluator.reset_state()
            else:
                logger.warning(f"Spoof detected. Score: {score:.2f}")
                self._fail("Liveness check failed. Spoof detected.")
                
            return self._build_ui_response(faces=faces)
            
        elif self.state.startswith("CHALLENGE_"):
            if time.time() - self.challenge_start_time > self.config['liveness']['challenge_timeout']:
                self._fail("Challenge timeout.")
                return self._build_ui_response()
                
            current_task = self.challenges[self.current_challenge_idx]
            task_passed = self.evaluator.evaluate_task(current_task, mp_data)
            
            if task_passed:
                self.frames_passed_for_current_task += 1
                if self.frames_passed_for_current_task >= self.config['liveness']['require_consecutive_frames']:
                    logger.info(f"Passed challenge: {current_task}")
                    self.current_challenge_idx += 1
                    self.frames_passed_for_current_task = 0
                    self.evaluator.reset_state()
                    self.challenge_start_time = time.time() # Reset timer for next challenge
                    
                    if self.current_challenge_idx >= 3:
                        self._succeed()
                    else:
                        self.state = f"CHALLENGE_{self.current_challenge_idx + 1}"
            else:
                # If they stop doing the gesture, reset the consecutive frames counter
                # Except for blinks which are stateful
                if 'blink' not in current_task:
                    self.frames_passed_for_current_task = 0
                    
            return self._build_ui_response(faces=faces)
            
        return self._build_ui_response()
        
    def _fail(self, reason):
        self.state = "FAIL"
        self.rejection_reason = reason
        logger.warning(f"Attendance rejected: {reason}")
        
    def _succeed(self):
        self.state = "SUCCESS"
        success, msg = self.db_manager.log_attendance(self.current_user['roll_number'])
        if not success:
            self.rejection_reason = msg
            self.state = "FAIL"
            logger.error(f"Failed to log attendance: {msg}")
            
    def _build_ui_response(self, faces=None):
        instruction = ""
        color = self.config['ui']['color_primary']
        
        if self.state == "IDLE":
            instruction = "Please look at the camera."
        elif self.state == "RECOGNIZING":
            instruction = "Recognizing face..."
        elif self.state == "LIVENESS":
            instruction = "Analyzing liveness..."
        elif self.state.startswith("CHALLENGE_"):
            task = self.challenges[self.current_challenge_idx]
            instruction = f"Task {self.current_challenge_idx + 1}/3: {task.replace('_', ' ').upper()}"
        elif self.state == "FAIL":
            instruction = f"ACCESS DENIED: {self.rejection_reason}"
            color = self.config['ui']['color_danger']
        elif self.state == "SUCCESS":
            instruction = f"ACCESS GRANTED: {self.current_user['name']}"
            color = self.config['ui']['color_success']
            
        return {
            'state': self.state,
            'instruction': instruction,
            'color': color,
            'faces': faces if faces else []
        }
