import os
import cv2
from pathlib import Path
from src.vision.insightface_wrapper import FaceAnalyzer

def extract_frames_and_crop(video_path, output_dir, label, analyzer, skip_frames=5):
    """
    Extracts frames from a video, detects faces, crops them, and saves to the output directory.
    label: "live" or "spoof"
    """
    cap = cv2.VideoCapture(video_path)
    count = 0
    frame_id = 0
    
    os.makedirs(output_dir, exist_ok=True)
    video_name = Path(video_path).stem
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if frame_id % skip_frames == 0:
            faces = analyzer.analyze_frame(frame)
            if len(faces) > 0:
                # Assume largest face is the target
                face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
                bbox = face.bbox.astype(int)
                
                # Add margin
                x1, y1 = max(0, bbox[0]-20), max(0, bbox[1]-20)
                x2, y2 = min(frame.shape[1], bbox[2]+20), min(frame.shape[0], bbox[3]+20)
                
                face_crop = frame[y1:y2, x1:x2]
                
                if face_crop.size > 0:
                    out_path = os.path.join(output_dir, f"{video_name}_{count}.jpg")
                    cv2.imwrite(out_path, face_crop)
                    count += 1
                    
        frame_id += 1
        
    cap.release()
    print(f"Extracted {count} faces from {video_name}")

if __name__ == "__main__":
    # Example usage
    # analyzer = FaceAnalyzer(name='buffalo_l')
    # extract_frames_and_crop("datasets/casia/live/1.avi", "datasets/processed/live", "live", analyzer)
    pass
