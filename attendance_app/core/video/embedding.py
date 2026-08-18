# # from arcface import ArcFace

# # def get_face_embedding(array_of_images):
# #     face_rec = ArcFace.ArcFace()
# #     # Array of images: face_rec.calc_emb(["test1.jpg", "test2.png"])
# #     embedding_of_all_images =face_rec.calc_emb(array_of_images)
# #     # We now store his embedding in the vector db for future use.
# #     return embedding_of_all_images

# from attrs import inspect
# from deepface import DeepFace
# import base64
# from io import BytesIO
# from PIL import Image
# import numpy as np
# import retinaface

# def get_face_embedding(array_of_images):
#     embeddings = []
#     for img_data in array_of_images:
#         # img_data is base64 without prefix
#         img_bytes = base64.b64decode(img_data)
#         img = Image.open(BytesIO(img_bytes))
#         img_np = np.array(img)
#         print(f"    Image in get face embedding function: {img_np}")
#         # print(inspect.signature(DeepFace.represent))
#         # embedding = DeepFace.represent(
#         #     img_path=img_np,
#         #     detector_backend = 'retinaface', 
#         #     align = True
#         #     # model_name="ArcFace",
#         #     # detection_model="RetinaFace"  # optional but recommended
#         # )
#         embedding = DeepFace.represent(
#             img_path=img_np,
#             detector_backend='yunet',
#             align=True,
#             model_name="SFace",        # faster than ArcFace
#             distance_metric="euclidean_l2"
#         )
#         for face in embedding:
#             if isinstance(face, dict):
#                 # Use "embedding" or "vector" depending on your DeepFace version
#                 emb = face.get("embedding") or face["vector"]
#                 embeddings.append(emb)
#             elif isinstance(face, np.ndarray):
#                 embeddings.append(face.tolist())
#             # embeddings.append(embedding)
#     print(f"    Embeddings in get face embedding function: {embeddings}")
#     return 

import base64
from io import BytesIO
from PIL import Image
import numpy as np
from deepface import DeepFace
from retinaface import RetinaFace

def get_face_embedding(array_of_images, detector_backend="yunet", model_name="ArcFace"):
    embeddings = []

    for img_data in array_of_images:
        img_bytes = base64.b64decode(img_data)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img)

        faces = RetinaFace.extract_faces(
            img_path=img_np,
            align=True
        )
        if len(faces) == 0:
            print("No face detected.")
            continue

        if len(faces) > 1:
            print("Multiple faces detected. Please stand alone.")
            continue
        embedding_result = DeepFace.represent(
            img_path=faces,
            detector_backend="skip",
            model_name="ArcFace",
            enforce_detection=False
        )
        print("embedding_result",embedding_result)
        for face in embedding_result:
            if isinstance(face, dict):
                emb = face.get("embedding") or face.get("vector")
                embeddings.append(emb)
            elif isinstance(face, np.ndarray):
                embeddings.append(face.tolist())
        print("embeddings",embeddings[0])
    return embeddings[0]