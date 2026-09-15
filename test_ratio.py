import cv2
import mediapipe as mp
import math

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

print("Starting camera to test ratio. Press q to quit.")
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    
    if results.multi_face_landmarks:
        lms = results.multi_face_landmarks[0]
        nose = lms.landmark[1]
        left_eye = lms.landmark[133]
        right_eye = lms.landmark[362]
        
        d_left = abs(nose.x - left_eye.x)
        d_right = abs(nose.x - right_eye.x)
        ratio = d_left / (d_right + 1e-6)
        
        print(f"Ratio: {ratio:.2f} | D_left: {d_left:.4f}, D_right: {d_right:.4f}")
        
    cv2.imshow("Test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()
