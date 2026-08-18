import chromadb
from chromadb import Client
from user.utils import compute_result_data
from core.video.capture import convert_video_to_embedding
import random
import string
import numpy as np
# client = chromadb.PersistentClient(path="./chroma_db")
client = chromadb.PersistentClient(path="./chroma_db")

EMPLOYEE_COLLECTION = "employee_faces_512"
# client = Client()
# collection = client.get_or_create_collection(
#     name="employee_faces"
# )  Since we already created the collectin we need not create it again

EXPECTED_FACE_DIMENSION = 512  # ArcFace
# Use 128 if your collection was built with SFace.

# To Flatten the List
def flatten_single_embedding(face_embedding):
    """
    Convert input into one flat face vector.

    Accepted shapes:
        [512]
        [[512]]
        [[[512]]]

    Returns:
        [512]
    """

    if face_embedding is None:
        raise ValueError("face_embedding is None.")

    vector = np.asarray(
        face_embedding,
        dtype=np.float32,
    ).reshape(-1)

    if vector.size == 0:
        raise ValueError("face_embedding is empty.")

    if vector.size != EXPECTED_FACE_DIMENSION:
        raise ValueError(
            f"Expected {EXPECTED_FACE_DIMENSION}-dimensional "
            f"embedding, got {vector.size}. "
            f"Original shape: "
            f"{np.asarray(face_embedding).shape}"
        )

    if not np.isfinite(vector).all():
        raise ValueError(
            "Embedding contains NaN or infinite values."
        )

    return vector.tolist()

def generate_employee_id():
    """
    Generate a random employee ID.
    
    Args:
        prefix: Prefix for the employee ID (default: "EMP").
        length: Number of random characters after the prefix (default: 6).
    
    Returns:
        A string like: EMP1A3B9C
    """
    prefix = "EMP"
    length = 6
    # Use uppercase letters and digits for the random part
    random_part = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )
    return f"{prefix}{random_part}"

def add_employee_to_vector_db(employee_data, embeddings):
    """
    embeddings: list of 5 face vectors (each a list of numbers).
    Store as 5 records, all with the same employee_id.
    """
    print("Adding employee to vector database...")
    print("embeddings type:", type(embeddings), "len:", len(embeddings) if isinstance(embeddings, list) else None)
    print("employee_data:", employee_data)

    collection = client.get_or_create_collection(name=EMPLOYEE_COLLECTION, metadata={"hnsw:space": "cosine"})

    # Flatten if needed
    if embeddings and isinstance(embeddings[0], list) and isinstance(embeddings[0][0], list):
        embeddings_list = [vec for vec_list in embeddings for vec in vec_list]
    elif isinstance(embeddings, list) and isinstance(embeddings[0], list):
        embeddings_list = embeddings
    else:
        embeddings_list = [embeddings]

    # Get or generate employee_id
    emp_id = employee_data.get("employee_id")
    if not emp_id:
        emp_id = generate_employee_id()

    ids = []
    embeddings_for_db = []
    metadatas = []

    for i, emb in enumerate(embeddings_list):
        ids.append(f"{emp_id}_face_{i}")
        embeddings_for_db.append(emb)
        metadatas.append({
            "employee_id": emp_id,
            # "name": f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}",
            # "department": str(employee_data.get("department", "")) or "",
            # "designation": str(employee_data.get("designation", "")) or "",
        })

    collection.add(
        ids=ids,
        embeddings=embeddings_for_db,
        metadatas=metadatas
    )

    print(f"Employee {emp_id} added to vector database with {len(embeddings_list)} embeddings.")

# def get_employee_from_vector_db(face_embeddings):
#     """
#     face_embeddings: list of face vectors (each is a list of numbers).
#     Returns: query results dict or None.
#     """
#     print("type of embeddings in the vector query function", type(face_embeddings))

#     collection = client.get_or_create_collection(name=EMPLOYEE_COLLECTION,metadata={"hnsw:space": "cosine"})

#     # Ensure we pass a list of vectors to query_embeddings
#     results = collection.query(
#         query_embeddings=face_embeddings,  # not [face_embeddings]
#         n_results=1,
#     )
#     if results and results["metadatas"]:
#         # results["metadatas"] is a list of lists
#         # first_metadata = results["metadatas"][0][0]
#         print(
#             f"Employee found in vector database. "
#             f"results: {results}"
#         )
#         # employee_id_from_result=results['metadatas'][0][0]['employee_id']
#         # return employee_id_from_result
#         result = compute_result_data(results)
#         print("Computed result data:", result['employee_id'], result['score'])
#         return result
#     else:
#         print("Employee not found in vector database.")
#         return None

COSINE_DISTANCE_THRESHOLD = 0.45

def get_employee_from_vector_db(face_embedding):
    """
    face_embedding: one face vector, for example [0.1, 0.2, ...]
    Returns:
        {
            "employee_id": "...",
            "distance": 0.12,
            "similarity": 0.88,
            "matched": True
        }
        or an unknown result.
    """
    try:
        query_vector = flatten_single_embedding(
            face_embedding
        )
    except (TypeError, ValueError) as exc:
        return {
            "employee_id": None,
            "distance": None,
            "similarity": None,
            "matched": False,
            "reason": f"Invalid face embedding: {exc}",
        }
    collection = client.get_or_create_collection(
        name=EMPLOYEE_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

    # Chroma expects a list of embeddings.
    results = collection.query(
        query_embeddings=[face_embedding],
        n_results=5,
        include=["metadatas", "distances"]
    )

    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not metadatas or not distances:
        return {
            "employee_id": None,
            "distance": None,
            "similarity": None,
            "matched": False,
            "reason": "No candidates found"
        }

    candidates = []

    for metadata, distance in zip(metadatas, distances):
        employee_id = metadata.get("employee_id")

        if employee_id is not None:
            candidates.append({
                "employee_id": employee_id,
                "distance": float(distance)
            })

    if not candidates:
        return {
            "employee_id": None,
            "distance": None,
            "similarity": None,
            "matched": False,
            "reason": "No employee metadata found"
        }

    # Chroma cosine distance: lower is better.
    best_match = min(candidates, key=lambda item: item["distance"])

    distance = best_match["distance"]
    similarity = 1.0 - distance
    matched = distance <= COSINE_DISTANCE_THRESHOLD

    if not matched:
        return {
            "employee_id": None,
            "distance": distance,
            "similarity": similarity,
            "matched": False,
            "reason": "Below recognition threshold"
        }

    return {
        "employee_id": best_match["employee_id"],
        "distance": distance,
        "similarity": similarity,
        "matched": True,
        "reason": "Match accepted"
    }
    
def delete_employee_collection():
    """
    Delete the entire 'employee_faces' collection from ChromaDB.
    This removes all data and metadata for that collection.
    """
    from chromadb import Client

    client = Client()

    collection_name = "employee_faces"

    # Check if collection exists
    try:
        collection = client.get_collection(name=collection_name)
        client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted successfully.")
    except Exception as e:
        # Collection might not exist
        print(f"Failed to delete collection '{collection_name}': {e}")

def get_all_employees_from_vector_db():
    """
    Retrieve all employee records from the 'employee_faces' collection.
    Returns a list of dictionaries containing employee data and embeddings.
    """
    collection = client.get_collection(name=EMPLOYEE_COLLECTION)
    collections = client.list_collections()
    # Query all records
    batch_size = 100
    get_data= collection.get(
        include=["embeddings", "metadatas"]
    )
    total = collection.count()
    for offset in range(0, total, batch_size):
        batch = collection.get(
            limit=batch_size,
            offset=offset
        )
    print(len(get_data["embeddings"]))
    print(len(get_data["metadatas"]))
    print(get_data["metadatas"])
    print(len(get_data["ids"]))
    print(batch["ids"])
    print(collections)
    print(collection.metadata)
    return "Got the Data"