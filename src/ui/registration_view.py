import customtkinter as ctk
import cv2
from PIL import Image
import numpy as np

class RegistrationView(ctk.CTkFrame):
    def __init__(self, master, db_manager, face_analyzer):
        super().__init__(master)
        self.db_manager = db_manager
        self.face_analyzer = face_analyzer
        
        # UI Elements
        self.title = ctk.CTkLabel(self, text="New Student Registration", font=("Helvetica", 24, "bold"))
        self.title.pack(pady=20)
        
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=20, fill="x")
        
        self.entries = {}
        fields = ["Name", "Roll Number", "Department", "Semester", "Section"]
        for field in fields:
            lbl = ctk.CTkLabel(self.form_frame, text=field)
            lbl.pack(pady=(10, 0))
            ent = ctk.CTkEntry(self.form_frame, width=300)
            ent.pack(pady=(0, 10))
            self.entries[field] = ent
            
        self.status_lbl = ctk.CTkLabel(self, text="", text_color="yellow")
        self.status_lbl.pack(pady=10)
        
        self.capture_btn = ctk.CTkButton(self, text="Capture & Register", command=self.start_registration)
        self.capture_btn.pack(pady=20)
        
    def start_registration(self):
        # Gather data
        data = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(data.values()):
            self.status_lbl.configure(text="Please fill all fields", text_color="red")
            return
            
        self.status_lbl.configure(text="Looking for face... Please look at the camera.", text_color="yellow")
        self.update()
        
        # Capture from camera
        cap = cv2.VideoCapture(0)
        embeddings = []
        frames_captured = 0
        target_frames = 10
        
        while frames_captured < target_frames:
            ret, frame = cap.read()
            if not ret: continue
            
            faces = self.face_analyzer.analyze_frame(frame)
            if len(faces) == 1:
                embeddings.append(faces[0].embedding)
                frames_captured += 1
                self.status_lbl.configure(text=f"Capturing... {frames_captured}/{target_frames}")
                self.update()
            elif len(faces) > 1:
                self.status_lbl.configure(text="Multiple faces detected! Please stand alone.", text_color="red")
                self.update()
                
        cap.release()
        
        # Average embeddings
        avg_embedding = np.mean(embeddings, axis=0)
        
        # Save to DB
        success, msg = self.db_manager.register_user(
            roll_number=data["Roll Number"],
            name=data["Name"],
            department=data["Department"],
            semester=data["Semester"],
            section=data["Section"],
            embedding=avg_embedding
        )
        
        if success:
            self.status_lbl.configure(text="Registration Successful!", text_color="green")
            for ent in self.entries.values(): ent.delete(0, 'end')
        else:
            self.status_lbl.configure(text=f"Error: {msg}", text_color="red")
