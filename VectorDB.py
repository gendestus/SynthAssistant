import chromadb
import chromadb.api.models.Collection
from chromadb.config import Settings
import datetime
import Memory
import uuid

class VectorDB:
    chroma_client: chromadb.Client
    collection: chromadb.api.models.Collection.Collection
    collection_name: str = "memories"

    def __init__(self, settings: Settings):
        self.chroma_client = chromadb.Client(settings)
        self.collection = self.chroma_client.get_or_create_collection(self.collection_name)

    def store(self, type, memory, importance):
        self.collection.add(
            documents=[memory.value],
            metadatas=[{"type":type, "timestamp":int(datetime.datetime.now().timestamp()), "importance":importance}],
            ids=[str(uuid.uuid4())]
        )
    def recall_important(self, n_expected):
        memories = []
        n_results = n_expected
        total_records = self.collection.count()
        if total_records < n_expected:
            n_results = total_records

        results = self.collection.get(
            limit = 1000,
            where={"importance": {"$gt": 0.5}},
        )
        
        ids = results["ids"]
        metadatas = results["metadatas"]
        documents = results["documents"]
        ids.reverse()
        metadatas.reverse()
        documents.reverse()

        for i in range(len(ids)):
            memory = Memory.Memory()
            memory.id = ids[i]
            memory.type = metadatas[i]["type"]
            memory.value = documents[i]
            memory.timestamp = metadatas[i]["timestamp"]
            memory.recall_trigger = None
            memory.importance = metadatas[i]["importance"]
            memories.append(memory)
            if i >= n_results:
                break
        return memories
    def recall_recent(self, n_expected):
        memories = []
        n_results = n_expected
        total_records = self.collection.count()
        if total_records < n_expected:
            n_results = total_records

        results = self.collection.get(
            limit = 1000,
            where={"timestamp": {"$gt": int(datetime.datetime.now().timestamp()) - 3600}},
        )
        
        ids = results["ids"]
        metadatas = results["metadatas"]
        documents = results["documents"]
        ids.reverse()
        metadatas.reverse()
        documents.reverse()
        
        for i in range(len(ids)):
            memory = Memory.Memory()
            memory.id = ids[i]
            memory.type = metadatas[i]["type"]
            memory.value = documents[i]
            memory.timestamp = metadatas[i]["timestamp"]
            memory.recall_trigger = None
            memory.importance = metadatas[i]["importance"]
            memories.append(memory)
            if i >= n_results:
                break

        return memories
    def recall_value(self, value, n_expected):
        memories = []
        n_results = n_expected
        total_records = self.collection.count()
        if total_records < n_expected:
            n_results = total_records

        results = self.collection.query(
            query_texts=[value],
            n_results = n_results
        )   
        n_returned = len(results["ids"][0])

        for i in range(n_returned):
            memory = Memory.Memory()
            memory.id = results["ids"][0][i]
            memory.type = results["metadatas"][0][i]["type"]
            memory.value = results["documents"][0][i]
            memory.timestamp = results["metadatas"][0][i]["timestamp"]
            memory.recall_trigger = value
            memory.distance = results["distances"][0][i]
            memory.importance = results["metadatas"][0][i]["importance"]
            memories.append(memory)
        return memories
    
    def wipe_memory(self):
        self.chroma_client.reset()



        
    