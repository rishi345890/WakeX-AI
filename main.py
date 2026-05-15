import cv2
import mediapipe as mp
import math
import tkinter as tk
from PIL import Image, ImageTk
from pygame import mixer

# ==========================================
# WAKEX AI - ADVANCED DRIVER MONITORING
# ==========================================

# ------------------------------------------
# ALARM SETUP
# ------------------------------------------
mixer.init()
mixer.music.load("alarm.mp3")

# ------------------------------------------
# MEDIAPIPE SETUP
# ------------------------------------------
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True,
    max_num_faces=1
)

# ------------------------------------------
# CAMERA
# ------------------------------------------
cap = cv2.VideoCapture(0)

# ------------------------------------------
# VARIABLES
# ------------------------------------------
sleep_frames = 0
yawn_frames = 0
driver_score = 100
status_text = "ACTIVE"

# ==========================================
# DISTANCE FUNCTION
# ==========================================
def calculate_distance(point1, point2):

    return math.hypot(
        point2.x - point1.x,
        point2.y - point1.y
    )

# ==========================================
# TKINTER GUI
# ==========================================
root = tk.Tk()

root.title("WakeX AI System")
root.geometry("1200x800")
root.configure(bg="black")

# ==========================================
# TITLE
# ==========================================
title = tk.Label(
    root,
    text="WakeX AI Driver Drowsiness Detection",
    font=("Arial", 24, "bold"),
    fg="cyan",
    bg="black"
)

title.pack(pady=10)

# ==========================================
# VIDEO LABEL
# ==========================================
video_label = tk.Label(root)
video_label.pack()

# ==========================================
# STATUS LABEL
# ==========================================
status_label = tk.Label(
    root,
    text="STATUS: ACTIVE",
    font=("Arial", 18, "bold"),
    fg="lime",
    bg="black"
)

status_label.pack(pady=10)

# ==========================================
# SCORE LABEL
# ==========================================
score_label = tk.Label(
    root,
    text="DRIVER SCORE: 100",
    font=("Arial", 16, "bold"),
    fg="white",
    bg="black"
)

score_label.pack()

# ==========================================
# UPDATE FRAME FUNCTION
# ==========================================
def update_frame():

    global sleep_frames
    global yawn_frames
    global driver_score
    global status_text

    success, frame = cap.read()

    if success:

        # Mirror effect
        frame = cv2.flip(frame, 1)

        # ==========================================
        # NIGHT MODE
        # ==========================================
        frame = cv2.convertScaleAbs(
            frame,
            alpha=1.4,
            beta=30
        )

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = face_mesh.process(rgb_frame)

        # ==========================================
        # FACE DETECTION
        # ==========================================
        if results.multi_face_landmarks:

            for face_landmarks in results.multi_face_landmarks:

                landmarks = face_landmarks.landmark

                # ----------------------------------
                # EYES
                # ----------------------------------
                left_top = landmarks[159]
                left_bottom = landmarks[145]

                right_top = landmarks[386]
                right_bottom = landmarks[374]

                # ----------------------------------
                # MOUTH
                # ----------------------------------
                upper_lip = landmarks[13]
                lower_lip = landmarks[14]

                # ----------------------------------
                # NOSE
                # ----------------------------------
                nose = landmarks[1]

                # ==========================================
                # EYE DISTANCE
                # ==========================================
                left_eye_distance = calculate_distance(
                    left_top,
                    left_bottom
                )

                right_eye_distance = calculate_distance(
                    right_top,
                    right_bottom
                )

                eye_distance = (
                    left_eye_distance +
                    right_eye_distance
                ) / 2

                # ==========================================
                # MOUTH DISTANCE
                # ==========================================
                mouth_distance = calculate_distance(
                    upper_lip,
                    lower_lip
                )

                # ==========================================
                # DROWSINESS DETECTION
                # ==========================================
                if eye_distance < 0.012:

                    sleep_frames += 1
                    driver_score -= 1

                else:

                    sleep_frames = 0
                    mixer.music.stop()

                # ==========================================
                # SLEEP ALERT
                # ==========================================
                if sleep_frames > 15:

                    status_text = "DROWSY"

                    cv2.putText(
                        frame,
                        "WAKE UP DRIVER!",
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 0, 255),
                        4
                    )

                    # ALARM
                    if not mixer.music.get_busy():
                        mixer.music.play()

                    # SAVE SCREENSHOT
                    cv2.imwrite(
                        "sleep_detected.jpg",
                        frame
                    )

                # ==========================================
                # YAWNING DETECTION
                # ==========================================
                elif mouth_distance > 0.05:

                    yawn_frames += 1
                    driver_score -= 1

                    status_text = "YAWNING"

                    cv2.putText(
                        frame,
                        "YAWNING DETECTED!",
                        (50, 160),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        3
                    )

                else:
                    yawn_frames = 0
                    status_text = "ACTIVE"

                # ==========================================
                # HEAD POSE DETECTION
                # ==========================================
                if nose.y > 0.60:

                    cv2.putText(
                        frame,
                        "HEAD DOWN!",
                        (50, 220),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 255),
                        3
                    )

                # ==========================================
                # SCORE LIMIT
                # ==========================================
                if driver_score < 0:
                    driver_score = 0

                # ==========================================
                # DISPLAY STATUS
                # ==========================================
                cv2.putText(
                    frame,
                    f"STATUS: {status_text}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    3
                )

                # ==========================================
                # DISPLAY SCORE
                # ==========================================
                cv2.putText(
                    frame,
                    f"SCORE: {driver_score}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2
                )

        # ==========================================
        # CONVERT IMAGE FOR TKINTER
        # ==========================================
        img = Image.fromarray(rgb_frame)

        imgtk = ImageTk.PhotoImage(image=img)

        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        # ==========================================
        # UPDATE LABELS
        # ==========================================
        status_label.config(
            text=f"STATUS: {status_text}"
        )

        score_label.config(
            text=f"DRIVER SCORE: {driver_score}"
        )

    root.after(10, update_frame)

# ==========================================
# START FUNCTION
# ==========================================
def start_system():

    update_frame()

# ==========================================
# EXIT FUNCTION
# ==========================================
def exit_system():

    cap.release()
    root.destroy()

# ==========================================
# BUTTON FRAME
# ==========================================
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=20)

# ==========================================
# START BUTTON
# ==========================================
start_btn = tk.Button(
    button_frame,
    text="START SYSTEM",
    font=("Arial", 14, "bold"),
    bg="green",
    fg="white",
    padx=20,
    pady=10,
    command=start_system
)

start_btn.grid(row=0, column=0, padx=20)

# ==========================================
# EXIT BUTTON
# ==========================================
exit_btn = tk.Button(
    button_frame,
    text="EXIT",
    font=("Arial", 14, "bold"),
    bg="red",
    fg="white",
    padx=20,
    pady=10,
    command=exit_system
)

exit_btn.grid(row=0, column=1, padx=20)

# ==========================================
# MAIN LOOP
# ==========================================
root.mainloop()