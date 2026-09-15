import math
import numpy as np

class ChallengeEvaluator:
    """Evaluates frame-by-frame data from MediaPipe to verify if a challenge was passed."""
    
    def __init__(self):
        self.prev_head_state = "unknown"
        self.reset_state()
        
    def reset_state(self):
        self.blink_count = 0
        self.prev_eye_state = "open"
        self.turn_count = 0
        self.ema_ear = 0.0
        # Notice we do NOT reset prev_head_state here! 
        # It must persist across tasks to prevent auto-bypassing if the user holds a turned head.

    def _get_eye_aspect_ratio(self, eye_indices, face_landmarks):
        """Calculates EAR to detect blinks."""
        # eye_points are indices for upper/lower and left/right corners of the eye
        if not face_landmarks:
            return 0.0
            
        p = [face_landmarks.landmark[i] for i in eye_indices]
        
        # Vertical distances
        v1 = math.hypot(p[1].x - p[5].x, p[1].y - p[5].y)
        v2 = math.hypot(p[2].x - p[4].x, p[2].y - p[4].y)
        # Horizontal distance
        h = math.hypot(p[0].x - p[3].x, p[0].y - p[3].y)
        
        ear = (v1 + v2) / (2.0 * h) if h != 0 else 0
        return ear

    def evaluate_task(self, task_name: str, mp_data: dict) -> bool:
        """
        Evaluates a specific task against the current frame's mediapipe data.
        Returns True if the task is successfully completed in this frame sequence.
        """
        face_lms = mp_data.get('face_landmarks')
        hand_lms = mp_data.get('hand_landmarks')
        
        current_head_state = "unknown"
        
        # --- GLOBAL HEAD STATE TRACKING ---
        if face_lms:
            current_head_state = "centered"
            nose_tip = face_lms.landmark[1]
            user_left_eye = face_lms.landmark[33]
            user_right_eye = face_lms.landmark[263]
            
            dist_to_left = abs(nose_tip.x - user_left_eye.x)
            dist_to_right = abs(nose_tip.x - user_right_eye.x)
            
            # If the nose is significantly closer to one eye than the other, the head is turned.
            # 0.75 ensures the head is actually turned visibly (prevents micro-jitter auto-passing)
            if dist_to_left < (dist_to_right * 0.75) or dist_to_right < (dist_to_left * 0.75):
                current_head_state = "sideways"
                
            # Only count a turn if they transition from centered to sideways!
            if self.prev_head_state == "centered" and current_head_state == "sideways":
                self.turn_count += 1
                
            self.prev_head_state = current_head_state

        # 1. EYE CHALLENGES
        if task_name in ['blink_once', 'blink_twice']:
            if not face_lms: return False
            
            # Simplified indices for Left and Right Eye
            LEFT_EYE = [33, 160, 158, 133, 153, 144]
            RIGHT_EYE = [362, 385, 387, 263, 373, 380]
            
            left_ear = self._get_eye_aspect_ratio(LEFT_EYE, face_lms)
            right_ear = self._get_eye_aspect_ratio(RIGHT_EYE, face_lms)
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Initialize EMA (Exponential Moving Average) on first frame
            if self.ema_ear == 0.0:
                self.ema_ear = avg_ear
            else:
                # ONLY adapt if the eye is wide open or barely moving (prevent tracking the blink downwards)
                if avg_ear >= self.ema_ear * 0.95:
                    self.ema_ear = 0.90 * self.ema_ear + 0.10 * avg_ear
            
            # A true blink is just a 15% drop from their moving average resting state.
            thresh = self.ema_ear * 0.85
            
            current_eye_state = "closed" if avg_ear < thresh else "open"
            
            if self.prev_eye_state == "closed" and current_eye_state == "open":
                self.blink_count += 1
                
            self.prev_eye_state = current_eye_state
            
            if task_name == 'blink_once' and self.blink_count >= 1: return True
            if task_name == 'blink_twice' and self.blink_count >= 2: return True
            
        # 2. HEAD POSES
        elif task_name in ['look_left', 'look_right']:
            if not face_lms: return False
            # Accept ANY direction turn (left or right).
            # This completely eliminates user confusion about mirror-image directions.
            # Because we require turn_count >= 1, they MUST return to center between tasks, preventing auto-bypass.
            if self.turn_count >= 1:
                return True
                
        elif task_name in ['look_up', 'look_down']:
            if not face_lms: return False
            
            nose_tip = face_lms.landmark[1]
            left_ear_y = face_lms.landmark[234].y
            right_ear_y = face_lms.landmark[454].y
            ear_y_avg = (left_ear_y + right_ear_y) / 2.0
            
            if task_name == 'look_up' and nose_tip.y < (ear_y_avg - 0.005): return True
            if task_name == 'look_down' and nose_tip.y > (ear_y_avg + 0.015): return True
            
        # 3. HAND CHALLENGES
        elif task_name == 'raise_open_palm':
            if hand_lms:
                for hand in hand_lms:
                    wrist = hand.landmark[0]
                    index_tip = hand.landmark[8]
                    middle_tip = hand.landmark[12]
                    mcp = hand.landmark[9] # Middle finger base
                    
                    # Size of the palm
                    palm_size = math.hypot(mcp.x - wrist.x, mcp.y - wrist.y)
                    
                    # Distance of extended fingers
                    index_dist = math.hypot(index_tip.x - wrist.x, index_tip.y - wrist.y)
                    middle_dist = math.hypot(middle_tip.x - wrist.x, middle_tip.y - wrist.y)
                    
                    # Fingers must be visibly extended (prevents auto-passing just by showing a hand)
                    if index_dist > (palm_size * 1.5) and middle_dist > (palm_size * 1.5):
                        return True

        elif task_name == 'thumbs_up':
            if hand_lms:
                for hand in hand_lms:
                    wrist = hand.landmark[0]
                    thumb_tip = hand.landmark[4]
                    index_tip = hand.landmark[8]
                    
                    # Distance from wrist to thumb tip
                    thumb_dist = math.hypot(thumb_tip.x - wrist.x, thumb_tip.y - wrist.y)
                    # Distance from wrist to index tip
                    index_dist = math.hypot(index_tip.x - wrist.x, index_tip.y - wrist.y)
                    
                    # Thumb must be extended relative to folded index finger
                    if thumb_dist > (index_dist * 1.4): 
                        return True
                    
        # 4. FACE CHALLENGES
        elif task_name == 'smile':
            if not face_lms: return False
            # Distance between mouth corners (61 and 291)
            mouth_left = face_lms.landmark[61]
            mouth_right = face_lms.landmark[291]
            mouth_width = math.hypot(mouth_left.x - mouth_right.x, mouth_left.y - mouth_right.y)
            # Distance between eyes for normalization
            eye_dist = math.hypot(face_lms.landmark[33].x - face_lms.landmark[263].x, face_lms.landmark[33].y - face_lms.landmark[263].y)
            
            if eye_dist > 0:
                ratio = mouth_width / eye_dist
                if ratio > 0.55: # Forgiving threshold for real smile
                    return True
                
        elif task_name == 'neutral_face':
            if not face_lms: return False
            mouth_left = face_lms.landmark[61]
            mouth_right = face_lms.landmark[291]
            mouth_width = math.hypot(mouth_left.x - mouth_right.x, mouth_left.y - mouth_right.y)
            eye_dist = math.hypot(face_lms.landmark[33].x - face_lms.landmark[263].x, face_lms.landmark[33].y - face_lms.landmark[263].y)
            
            # Ensure mouth is not smiling
            if eye_dist > 0 and (mouth_width / eye_dist) < 0.55: 
                return True 
            
        return False
