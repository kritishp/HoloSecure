# HoloSecure Attendance System

An AI-Powered Multi-Layer Anti-Spoof Attendance System with Interactive Verification.

## Architecture & Features

This system replaces simple (and easily spoofable) 2D face recognition attendance systems with a multi-layered verification pipeline:
1. **Face Detection**: Uses RetinaFace for robust face detection. Rejects multiple faces.
2. **Face Recognition**: Uses ArcFace to generate 512-d embeddings.
3. **CNN Liveness Detection**: Uses EfficientNet-B0 to analyze the cropped face for presentation attacks (printed photos, phones).
4. **Interactive Verification (Challenges)**: Uses MediaPipe (Hands and FaceMesh) to ensure the user is physically present and responsive by asking them to complete 3 randomized tasks (e.g., Blink twice, Raise open palm, Look left).

## Setup & Installation

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Download Models:
   - Ensure you have `buffalo_l` insightface model downloaded (InsightFace usually downloads this automatically on first run to `~/.insightface`).
   - Train the Liveness model (or place pretrained weights at `models/efficientnet_b0_antispoof.pth`).

3. Run the App:
   ```bash
   python main.py
   ```

## Training the Anti-Spoof Model

1. Place your CASIA-FASD or OULU-NPU videos in a directory.
2. Modify and run `train/dataset_prep.py` to extract cropped faces into `train/live` and `train/spoof` folders.
3. Run `python train/train_antispoof.py` to fine-tune the EfficientNet-B0 model.
