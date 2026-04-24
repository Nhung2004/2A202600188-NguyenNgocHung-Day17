import json
import os
import tiktoken
from typing import List, Dict, Any, Optional

class BaseMemory:
    def save(self, data: Any):
        pass
    def retrieve(self, query: str) -> Any:
        pass

class TokenCounter:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count(self, text: str) -> int:
        return len(self.encoding.encode(text))

class ShortTermMemory(BaseMemory):
    def __init__(self, max_tokens: int = 1000):
        self.history = []
        self.max_tokens = max_tokens
        self.token_counter = TokenCounter()
    
    def save(self, message: Dict[str, str]):
        self.history.append(message)
        self._trim()
    
    def _trim(self):
        while self.history and self.get_total_tokens() > self.max_tokens:
            self.history.pop(0)
            
    def get_total_tokens(self) -> int:
        return sum(self.token_counter.count(m["content"]) for m in self.history)
    
    def retrieve(self, limit: int = 10) -> List[Dict[str, str]]:
        return self.history[-limit:]

class LongTermMemory(BaseMemory):
    def __init__(self, filepath: str = "data/profile.json"):
        self.filepath = filepath
        # Đảm bảo thư mục data tồn tại
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.data = self._load()
    
    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_to_disk(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def save(self, key: str, value: Any):
        self.data[key] = value
        self._save_to_disk()
    
    def retrieve(self, key: str) -> Optional[Any]:
        return self.data.get(key)
    
    def get_all(self) -> Dict[str, Any]:
        return self.data

class EpisodicMemory(BaseMemory):
    def __init__(self, filepath: str = "data/episodes.jsonl"):
        self.filepath = filepath
        # Đảm bảo thư mục data tồn tại
        if os.path.dirname(self.filepath):
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
    
    def save(self, episode: Dict[str, Any]):
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(episode, ensure_ascii=False) + "\n")
    
    def retrieve(self, limit: int = 3) -> List[Dict[str, Any]]:
        episodes = []
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    episodes.append(json.loads(line))
        return episodes[-limit:]

class SemanticMemory(BaseMemory):
    def __init__(self, collection_name: str = "knowledge"):
        import chromadb
        from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
        
        class MockEmbeddingFunction(EmbeddingFunction):
            def __call__(self, input: Documents) -> Embeddings:
                return [[0.1] * 384 for _ in input]
        
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=MockEmbeddingFunction()
        )
    
    def save(self, text: str, metadata: Dict[str, Any] = None, doc_id: str = None):
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[doc_id or str(hash(text))]
        )
    
    def retrieve(self, query: str, n_results: int = 2) -> List[str]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

class MemoryRouter:
    @staticmethod
    def route(query: str) -> List[str]:
        query_lower = query.lower()
        targets = ["short-term"]
        if any(word in query_lower for word in ["tôi là", "tên tôi", "thích", "dị ứng", "sống ở", "ten toi", "di ung", "song o", "thich", "chuyển", "chuyen", "ở đâu", "o dau"]):
            targets.append("long-term")
        if any(word in query_lower for word in ["trước đây", "lần trước", "đã làm", "kết quả", "lan truoc", "da lam"]):
            targets.append("episodic")
        if any(word in query_lower for word in ["là gì", "định nghĩa", "hướng dẫn", "làm sao để", "la gi", "dinh nghia", "huong dan", "lam sao de", "docker", "database"]):
            targets.append("semantic")
        return list(set(targets))

class MemorySystem:
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.router = MemoryRouter()
        self.semantic.save("Docker service name for local development is 'web-app'.", {"type": "lesson"})
        self.semantic.save("To reset the database, use 'npm run db:reset'.", {"type": "manual"})
