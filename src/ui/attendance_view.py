import customtkinter as ctk
import cv2
from PIL import Image
import threading
from src.engine.decision_engine import DecisionEngine
from src.vision.mediapipe_tracker import MediaPipeTracker
from src.utils.logger import setup_logger

logger = setup_logger("AttendanceView")

class AttendanceView(ctk.CTkFrame):
    def __init__(self, master, db_manager, face_analyzer, liveness, config):
        super().__init__(master)
        self.config = config
        
        self.engine = DecisionEngine(db_manager, face_analyzer, liveness, config)
        self.mp_tracker = MediaPipeTracker()
        
        # UI Elements
        self.title = ctk.CTkLabel(self, text="HoloSecure Verification", font=("Helvetica", 28, "bold"), text_color=config['ui']['color_primary'])
        self.title.pack(pady=10)
        
        # Action buttons
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)
        
        self.reset_btn = ctk.CTkButton(self.btn_frame, text="Reset Session", command=self.reset_session)
        self.reset_btn.pack(side="left", padx=10)
        
        self.export_btn = ctk.CTkButton(self.btn_frame, text="Export to CSV", command=self.export_csv)
        self.export_btn.pack(side="left", padx=10)
        
        # Status text
        self.status_label = ctk.CTkLabel(self, text="Initializing...", font=("Helvetica", 20))
        self.status_label.pack(pady=10)
        
        # Video feed
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(pady=10)
        
        self._init_camera(config)
        
    def export_csv(self):
        success, msg = self.engine.db_manager.export_to_csv(self.config['database']['csv_export_dir'])
        if success:
            self.status_label.configure(text=f"Exported to {msg}", text_color=self.config['ui']['color_success'])
        else:
            self.status_label.configure(text=f"Export failed: {msg}", text_color=self.config['ui']['color_danger'])
        
    def _init_camera(self, config):
        self.cap = cv2.VideoCapture(config['camera']['index'])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['resolution'][0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['resolution'][1])
        
        self.running = True
        self.update_loop()
        
    def reset_session(self):
        self.engine.reset_session()
        
    def update_loop(self):
        if not self.running:
            return
            
        ret, frame = self.cap.read()
        if ret:
            # Process mediapipe (requires RGB)
            mp_data = self.mp_tracker.process_frame(frame)
            
            # Run decision engine
            ui_state = self.engine.process_frame(frame, mp_data)
            
            # Draw bounding boxes from UI state
            if ui_state.get('faces'):
                for face in ui_state['faces']:
                    bbox = face.bbox.astype(int)
                    # Use color from state
                    hex_color = ui_state['color'].lstrip('#')
                    bgr_color = tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), bgr_color, 2)
            
            # Update UI labels
            self.status_label.configure(text=ui_state['instruction'], text_color=ui_state['color'])
            
            # Convert frame for Tkinter
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            
            # Resize for display
            img = img.resize((800, 600))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 600))
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img
            
        self.after(30, self.update_loop)
        
    def destroy(self):
        self.running = False
        self.cap.release()
        self.mp_tracker.close()
        super().destroy()
