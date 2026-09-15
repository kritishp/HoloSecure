import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import cv2
import numpy as np
import os
from src.utils.logger import setup_logger

logger = setup_logger("LivenessDetector")

class AntiSpoofModel(nn.Module):
    def __init__(self):
        super(AntiSpoofModel, self).__init__()
        # Load EfficientNet-B0 and modify final layer for binary classification
        weights = models.EfficientNet_B0_Weights.DEFAULT
        self.model = models.efficientnet_b0(weights=weights)
        num_ftrs = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(num_ftrs, 1) # Output raw logits for 1 class
        
    def forward(self, x):
        return self.model(x)

class LivenessDetector:
    """Wrapper for the PyTorch EfficientNet-B0 anti-spoof model."""
    
    def __init__(self, model_path: str = "models/efficientnet_b0_antispoof.pth", threshold: float = 0.85):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        self.threshold = threshold
        self.model_path = model_path
        
        self.model = AntiSpoofModel()
        if os.path.exists(model_path):
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info(f"Loaded AntiSpoof weights from {model_path} onto {self.device}")
            except Exception as e:
                logger.error(f"Failed to load AntiSpoof weights: {e}")
        else:
            logger.warning(f"AntiSpoof weights not found at {model_path}. Using un-finetuned model (WILL NOT BE ACCURATE).")
            
        self.model.to(self.device)
        self.model.eval()
        
        # Preprocessing transforms expected by EfficientNet
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, face_crop: np.ndarray) -> float:
        """
        Takes a BGR face crop, runs it through EfficientNet, and returns a liveness score (0 to 1).
        1 = Live, 0 = Spoof.
        """
        try:
            if face_crop is None or face_crop.size == 0:
                return 0.0
                
            # Convert BGR (OpenCV) to RGB (PIL)
            img_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            
            # Apply transforms and add batch dimension
            input_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            
            # Predict
            with torch.no_grad():
                output = self.model(input_tensor)
                # If the model was trained such that 1=Spoof and 0=Live, we invert it here
                # so that the rest of the application can safely assume 1=Live.
                score = 1.0 - torch.sigmoid(output).item()
                
            return score
        except Exception as e:
            logger.error(f"Error during liveness prediction: {e}")
            return 0.0  # Fail safe to spoof on error
