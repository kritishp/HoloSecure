import cv2
import numpy as np
from insightface.app import FaceAnalysis
from src.utils.logger import setup_logger

logger = setup_logger("InsightFaceWrapper")

class FaceAnalyzer:
    """Wrapper for InsightFace's FaceAnalysis which handles RetinaFace and ArcFace."""
    
    def __init__(self, name: str = 'buffalo_l', det_thresh: float = 0.6, min_face_size: int = 100):
        self.app = FaceAnalysis(name=name, allowed_modules=['detection', 'recognition'])
        # Try to use GPU if available, else fallback to CPU
        self.app.prepare(ctx_id=0, det_thresh=det_thresh) # ctx_id=0 means GPU if available
        self.min_face_size = min_face_size
        logger.info(f"Initialized InsightFace '{name}' model.")
        
    def analyze_frame(self, frame: np.ndarray):
        """
        Analyzes a BGR frame, detecting faces and extracting embeddings.
        Returns a list of face objects.
        """
        if frame is None:
            return []
            
        faces = self.app.get(frame)
        valid_faces = []
        
        for face in faces:
            bbox = face.bbox.astype(int)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            
            if w >= self.min_face_size and h >= self.min_face_size:
                valid_faces.append(face)
                
        return valid_faces

    def compare_embeddings(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Computes cosine similarity between two embeddings."""
        emb1 = emb1.flatten()
        emb2 = emb2.flatten()
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(sim)
        
    def find_best_match(self, face_embedding: np.ndarray, known_users: list, threshold: float = 0.5):
        """
        Finds the best matching user from a list of known users.
        known_users should be a list of dicts with 'embedding' and 'roll_number'.
        """
        best_match = None
        highest_sim = -1.0
        
        for user in known_users:
            sim = self.compare_embeddings(face_embedding, user['embedding'])
            if sim > highest_sim:
                highest_sim = sim
                best_match = user
                
        if highest_sim >= threshold:
            return best_match, highest_sim
        return None, highest_sim
