from django.core.management.base import BaseCommand
import chromadb

COLLECTION_NAME = "employee_faces"


class Command(BaseCommand):
    help = "Creates the default ChromaDB collections."

    def handle(self, *args, **kwargs):
        client = chromadb.PersistentClient(path="./chroma_db")

        collections = client.list_collections()
        collection_names = [c.name for c in collections]

        if COLLECTION_NAME in collection_names:
            self.stdout.write(
                self.style.WARNING(
                    f"Collection '{COLLECTION_NAME}' already exists."
                )
            )
            return

        client.create_collection(name=COLLECTION_NAME)

        self.stdout.write(
            self.style.SUCCESS(
                f"Collection '{COLLECTION_NAME}' created successfully."
            )
        )