import chromadb

class ChromaManager:

    def get_or_create_collection(self, collection_name, metadata=None):
        try:
            collection = self.db.get_collection(f"collection_{collection_name}")
        except Exception as e:
            print(f"Collection '{collection_name}' not found. Creating it...")
            collection = self.db.create_collection(name=f"collection_{collection_name}", metadata=metadata)
        return collection

    def __init__(self,project_id):
        self.db = chromadb.HttpClient(host='vector_db')
        self.collection = self.get_or_create_collection(project_id)

    def save_graph(self, text_data, embeddings, ids):
        # Build a dictionary where each id maps to its latest document and embedding.
        combined = {}
        for doc, emb, _id in zip(text_data, embeddings, ids):
            # If the id already exists, update the entry; otherwise, create it.
            combined[_id] = (doc, emb)

        # Unpack the unique values.
        unique_ids = list(combined.keys())
        unique_texts, unique_embeddings = zip(*combined.values())

        # Use upsert if available. This will update existing entries and add new ones.
        self.collection.upsert(
            documents=list(unique_texts),
            embeddings=list(unique_embeddings),
            ids=unique_ids
        )

    def query(self, query_embededding, top_k=5):
        return self.collection.query(query_embeddings=query_embededding, n_results=top_k)

