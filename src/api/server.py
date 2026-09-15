import os
import cv2
import base64
import numpy as np
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List

from src.database.db_manager import DatabaseManager
from src.vision.insightface_wrapper import FaceAnalyzer
from src.vision.liveness import LivenessDetector
from src.vision.mediapipe_tracker import MediaPipeTracker
from src.engine.challenge_evaluator import ChallengeEvaluator
from src.engine.challenge_generator import ChallengeGenerator

app = FastAPI(title="HoloSecure API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_manager = None
face_analyzer = None
liveness_detector = None
mp_tracker = None
challenge_evaluator = None

@app.on_event("startup")
async def startup_event():
    global db_manager, face_analyzer, liveness_detector, mp_tracker, challenge_evaluator
    db_manager = DatabaseManager("database/attendance.db")
    face_analyzer = FaceAnalyzer(name="buffalo_l", det_thresh=0.6, min_face_size=100)
    liveness_detector = LivenessDetector(model_path="models/efficientnet_b0_antispoof.pth", threshold=0.85)
    mp_tracker = MediaPipeTracker()
    challenge_evaluator = ChallengeEvaluator()

class RegisterRequest(BaseModel):
    student_id: str
    name: str
    roll_number: str
    department: str
    semester: str
    section: str
    images: List[str]

@app.post("/api/register")
async def register_student(req: RegisterRequest):
    embeddings = []
    for b64_img in req.images:
        try:
            img_data = base64.b64decode(b64_img.split(",")[1] if "," in b64_img else b64_img)
            np_arr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            faces = face_analyzer.analyze_frame(img)
            if faces:
                embeddings.append(faces[0].embedding)
        except Exception as e:
            print(f"Error decoding image: {e}")
            
    if not embeddings:
        return {"success": False, "message": "No faces found in the provided images."}
        
    avg_embedding = np.mean(embeddings, axis=0)
    
    db_manager.register_user(
        roll_number=req.roll_number,
        name=req.name,
        department=req.department,
        semester=req.semester,
        section=req.section,
        embedding=avg_embedding
    )
    return {"success": True, "message": "Student registered successfully"}

@app.get("/api/tasks")
async def get_tasks():
    # Guarantee exactly 3 tasks as per prompt
    tasks = ChallengeGenerator.generate_challenges(count=3)
    if len(tasks) > 3: tasks = tasks[:3]
    return {"tasks": tasks}

@app.websocket("/ws/attendance")
async def attendance_ws(websocket: WebSocket):
    await websocket.accept()
    current_task = None
    liveness_history = []
    LIVENESS_HISTORY_LEN = 5
    max_avg_liveness = 0.0
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                payload = json.loads(data)
                
                b64_frame = payload.get("frame")
                client_task = payload.get("current_task")
                
                if client_task != current_task:
                    current_task = client_task
                    challenge_evaluator.reset_state()
                    max_avg_liveness = 0.0
                    liveness_history = []
                
                if not b64_frame:
                    continue
                    
                img_data = base64.b64decode(b64_frame.split(",")[1] if "," in b64_frame else b64_frame)
                np_arr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                response = {
                    "detected": False,
                    "bbox": None,
                    "recognition_confidence": 0,
                    "student": None,
                    "liveness_confidence": 0,
                    "task_passed": False
                }
                
                faces = face_analyzer.analyze_frame(img)
                known_users = db_manager.get_all_users()
                if faces:
                    best_face = faces[0]
                    response["detected"] = True
                    response["bbox"] = best_face.bbox.tolist()
                    
                    student_record, sim = face_analyzer.find_best_match(best_face.embedding, known_users, threshold=0.45)
                    
                    if student_record:
                        response["student"] = {"student_id": student_record['roll_number'], "name": student_record['name']}
                        response["recognition_confidence"] = float(sim)
                        
                    bbox = best_face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    w, h = x2 - x1, y2 - y1
                    
                    # Expand bbox by 40% to include phone bezels/edges for spoof context
                    pad_w, pad_h = int(w * 0.4), int(h * 0.4)
                    x1_exp, y1_exp = max(0, x1 - pad_w), max(0, y1 - pad_h)
                    x2_exp, y2_exp = min(img.shape[1], x2 + pad_w), min(img.shape[0], y2 + pad_h)
                    
                    face_crop = img[y1_exp:y2_exp, x1_exp:x2_exp]
                    
                    if face_crop.size > 0:
                        liveness_score = liveness_detector.predict(face_crop)
                    else:
                        liveness_score = 0
                        
                    liveness_history.append(float(liveness_score))
                    if len(liveness_history) > LIVENESS_HISTORY_LEN:
                        liveness_history.pop(0)
                        
                    avg_liveness = sum(liveness_history) / len(liveness_history)
                    max_avg_liveness = max(max_avg_liveness, avg_liveness)
                    
                    response["liveness_confidence"] = float(liveness_score)
                else:
                    response["detected"] = False
                    
                # Evaluate tasks using MediaPipe (which is robust to side profiles) independently of InsightFace
                mp_data = mp_tracker.process_frame(img)
                if current_task:
                    passed = challenge_evaluator.evaluate_task(current_task, mp_data)
                    
                    # Must have achieved high liveness at least once during this task
                    # 0.70 is the sweet spot: strict enough to block printed photos, but forgiving enough for real webcams
                    is_live = (max_avg_liveness >= 0.70)
                    response["task_passed"] = passed and is_live
                    response["evaluated_task"] = current_task
                
                await websocket.send_json(response)
            except WebSocketDisconnect:
                raise
            except RuntimeError as e:
                print(f"RuntimeError in websocket: {e}")
                break
            except Exception as e:
                import traceback
                print(f"Error in websocket loop: {e}")
                traceback.print_exc()
                
    except WebSocketDisconnect:
        pass

@app.post("/api/attendance/mark")
async def mark_attendance(req: dict):
    student_id = req.get("student_id")
    if student_id:
        # Note: Frontend currently sends student_id as roll_number. 
        # log_attendance expects roll_number.
        success, message = db_manager.log_attendance(student_id, status="Present")
        return {"success": success, "message": message}
    return {"success": False, "message": "No student ID provided"}

@app.get("/api/attendance/export")
async def export_attendance():
    success, result = db_manager.export_to_csv_string()
    if success:
        return Response(
            content=result,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=attendance_report.csv"}
        )
    return JSONResponse(status_code=500, content={"success": False, "message": result})

@app.get("/api/stats")
async def get_stats():
    return db_manager.get_stats()
