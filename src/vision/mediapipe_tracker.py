import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class DummyLandmarks:
    """Wrapper to mimic the old multi_face_landmarks[0] and multi_hand_landmarks[0] API."""
    def __init__(self, landmarks):
        self.landmark = landmarks

class MediaPipeTracker:
    """Wrapper for MediaPipe Face Mesh and Hands using Tasks API."""
    def __init__(self):
        base_options_face = python.BaseOptions(model_asset_path='models/face_landmarker.task')
        options_face = vision.FaceLandmarkerOptions(
            base_options=base_options_face,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
            min_face_detection_confidence=0.2,
            min_face_presence_confidence=0.2
        )
        self.face_landmarker = vision.FaceLandmarker.create_from_options(options_face)
        
        base_options_hands = python.BaseOptions(model_asset_path='models/hand_landmarker.task')
        options_hands = vision.HandLandmarkerOptions(
            base_options=base_options_hands,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5
        )
        self.hand_landmarker = vision.HandLandmarker.create_from_options(options_hands)
        
    def process_frame(self, frame: np.ndarray):
        """Processes the frame and returns landmarks for face and hands."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        face_results = self.face_landmarker.detect(mp_image)
        hand_results = self.hand_landmarker.detect(mp_image)
        
        face_landmarks = None
        if face_results.face_landmarks:
            face_landmarks = DummyLandmarks(face_results.face_landmarks[0])
            
        hand_landmarks = None
        if hand_results.hand_landmarks:
            hand_landmarks = [DummyLandmarks(hl) for hl in hand_results.hand_landmarks]
            
        return {
            'face_landmarks': face_landmarks,
            'hand_landmarks': hand_landmarks,
            'handedness': hand_results.handedness
        }
        
    def close(self):
        self.face_landmarker.close()
        self.hand_landmarker.close()
