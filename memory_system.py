import json
import os
from typing import List, Dict, Any, Optional
from collections import deque

class BaseMemory:
    def save(self, data: Any):
        pass
    def retrieve(self, query: str) -> Any:
        pass

class ShortTermMemory(BaseMemory):
    def __init__(self, max_size: int = 10):
        self.history = deque(maxlen=max_size)
    
    def save(self, message: Dict[str, str]):
        self.history.append(message)
    
    def retrieve(self, limit: int = 5) -> List[Dict[str, str]]:
        return list(self.history)[-limit:]

class LongTermMemory(BaseMemory):
    """Simulated Redis-style KV store using JSON"""
    def __init__(self, filepath: str = "profile.json"):
        self.filepath = filepath
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
    """JSON episodic log"""
    def __init__(self, filepath: str = "episodes.jsonl"):
        self.filepath = filepath
    
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
    """Mock semantic memory using keyword search to avoid downloading embedding models"""
    def __init__(self, collection_name: str = "knowledge"):
        self.documents = []
    
    def save(self, text: str, metadata: Dict[str, Any] = None, doc_id: str = None):
        self.documents.append({"text": text, "metadata": metadata or {}})
    
    def retrieve(self, query: str, n_results: int = 2) -> List[str]:
        query_words = set(query.lower().split())
        scored_docs = []
        for doc in self.documents:
            doc_words = set(doc["text"].lower().split())
            score = len(query_words.intersection(doc_words))
            if score > 0:
                scored_docs.append((score, doc["text"]))
        
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc[1] for doc in scored_docs[:n_results]]

class MemoryRouter:
    """Routes queries to appropriate memory backends"""
    @staticmethod
    def route(query: str) -> List[str]:
        query_lower = query.lower()
        targets = ["short-term"] # Always include short-term
        
        # Heuristic rules for routing
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
        
        # Add some initial semantic data for testing
        self.semantic.save("Docker service name for local development is 'web-app'.", {"type": "lesson"})
        self.semantic.save("To reset the database, use 'npm run db:reset'.", {"type": "manual"})
