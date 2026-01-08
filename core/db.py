from google.cloud import firestore

def get_db():
    """Authenticate using service account and return DB client."""
    return firestore.Client.from_service_account_json("ServiceAccountKey.json")


# ---------------------------
# USERS COLLECTION
# ---------------------------
def save_user(email, provider="password"):
    db = get_db()
    users = db.collection("users").document(email)

    users.set({
        "email": email,
        "provider": provider,
        "created_at": firestore.SERVER_TIMESTAMP
    })


def get_user(email):
    db = get_db()
    users = db.collection("users").document(email)
    return users.get().to_dict()


# ---------------------------
# DATASET METADATA COLLECTION
# ---------------------------
def save_dataset_metadata(email, filename, processed=False):
    db = get_db()
    collection = db.collection("datasets")

    collection.document(f"{email}_{filename}").set({
        "email": email,
        "filename": filename,
        "processed": processed,
        "timestamp": firestore.SERVER_TIMESTAMP
    })


def get_user_datasets(email):
    db = get_db()
    collection = db.collection("datasets")

    query = collection.where("email", "==", email).stream()
    return [doc.to_dict() for doc in query]


# ---------------------------
# JOB / PIPELINE TRACKING
# ---------------------------
def create_processing_job(email, status="pending"):
    db = get_db()
    jobs = db.collection("processing_jobs")

    job_ref = jobs.document()
    job_ref.set({
        "user": email,
        "status": status,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    return job_ref.id


def update_processing_job(job_id, status):
    db = get_db()
    ref = db.collection("processing_jobs").document(job_id)
    ref.update({"status": status})
