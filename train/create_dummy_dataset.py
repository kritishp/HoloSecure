import os
import cv2
import numpy as np

def create_dummy_data():
    base_dir = "datasets/processed/train"
    live_dir = os.path.join(base_dir, "live")
    spoof_dir = os.path.join(base_dir, "spoof")
    
    os.makedirs(live_dir, exist_ok=True)
    os.makedirs(spoof_dir, exist_ok=True)
    
    print("Generating dummy training data...")
    
    for i in range(100):
        # Create a mock "Live" face (e.g., a green circle)
        img_live = np.zeros((224, 224, 3), dtype=np.uint8)
        cv2.circle(img_live, (112, 112), 50, (0, 255, 0), -1)
        cv2.imwrite(os.path.join(live_dir, f"mock_live_{i}.jpg"), img_live)
        
        # Create a mock "Spoof" face (e.g., a red square)
        img_spoof = np.zeros((224, 224, 3), dtype=np.uint8)
        cv2.rectangle(img_spoof, (62, 62), (162, 162), (0, 0, 255), -1)
        cv2.imwrite(os.path.join(spoof_dir, f"mock_spoof_{i}.jpg"), img_spoof)
        
    print(f"Generated 100 live and 100 spoof images in {base_dir}")

if __name__ == "__main__":
    create_dummy_data()
