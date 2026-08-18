import cv2

# Initialize the default webcam (0 is usually the built-in webcam)
import cv2
from core.video.embedding import get_face_embedding

def convert_video_to_embedding(request=None):
    # if employee_data is not None:
    #     employee_data={
    #         "employee_id": request.employee_id,
    #         "first_name": request.first_name,
    #         "last_name": request.last_name,
    #         "department": request.department,
    #     "designation": request.designation,
    # }
    camera = cv2.VideoCapture(0)
    frames = []
    max_frames = 15

    if not camera.isOpened():
        print("Could not open webcam.")
        exit()

    print("Press SPACE to start capturing 15 frames.")
    print("Move your head slightly while capturing.")

    capturing = False

    while True:
        ret, frame = camera.read()
        if not ret:
            break
        cv2.imshow("Camera", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:      # ESC
            break
        elif key == 32:    # SPACE
            capturing = True
        if capturing:
            frames.append(frame.copy())
            print(f"Captured {len(frames)}/{max_frames}")

            # wait 300 ms before next capture
            cv2.waitKey(300)

            if len(frames) == max_frames:
                break

    camera.release()
    cv2.destroyAllWindows()
    face_embeddings = get_face_embedding(frames)
    print(f"\nCollected {len(frames)} frames.")
    return face_embeddings
# Up until here we saved all the frames in a list.
# Next step is to embed them. So we return embeddings here