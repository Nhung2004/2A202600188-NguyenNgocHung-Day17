from typing import TypedDict, List, Dict, Any, Annotated, Optional
from langgraph.graph import StateGraph, END
from core.memory_system import MemorySystem
import operator
import json
from pydantic import BaseModel, Field

class UserFacts(BaseModel):
    name: Optional[str] = Field(None, description="Tên người dùng")
    allergy: Optional[str] = Field(None, description="Dị ứng")
    hobby: Optional[str] = Field(None, description="Sở thích")
    location: Optional[str] = Field(None, description="Nơi ở")

class StructuredMemoryExtractor:
    def extract(self, query: str) -> UserFacts:
        query = query.lower()
        facts = {}
        if "tên tôi là" in query or "ten toi la" in query:
            prefix = "tên tôi là" if "tên tôi là" in query else "ten toi la"
            facts["name"] = query.split(prefix)[-1].strip().strip(".,!?").capitalize()
        if "dị ứng" in query or "di ung" in query:
            prefix = "dị ứng" if "dị ứng" in query else "di ung"
            if any(word in query for word in ["không phải", "nhầm", "khong phai", "nham"]):
                parts = query.split(prefix)
                if len(parts) > 1:
                    facts["allergy"] = parts[1].split("chứ không phải")[0].split("chu khong phai")[0].strip().strip(".,!?")
            else:
                facts["allergy"] = query.split(prefix)[-1].strip().strip(".,!?")
        if "thích" in query or "thich" in query and ("chơi" in query or "choi" in query):
            prefix = "chơi" if "chơi" in query else "choi"
            facts["hobby"] = query.split(prefix)[-1].strip().strip(".,!?")
        if any(word in query for word in ["sống ở", "song o", "chuyển", "chuyen"]):
            if any(word in query for word in ["không,", "chuyển", "khong,", "chuyen"]):
                temp = query
                for marker in ["vào", "vao"]:
                    if marker in temp: temp = temp.split(marker)[-1]
                for marker in ["rồi", "roi"]:
                    if marker in temp: temp = temp.split(marker)[0]
                facts["location"] = temp.strip().strip(".,!?").capitalize()
            else:
                prefix = "sống ở" if "sống ở" in query else "song o"
                facts["location"] = query.split(prefix)[-1].strip().strip(".,!?").capitalize()
        return UserFacts(**facts)

class MemoryState(TypedDict):
    messages: Annotated[List[Dict[str, str]], operator.add]
    user_profile: Dict[str, Any]
    episodes: List[Dict[str, Any]]
    semantic_hits: List[str]
    next_node: str
    current_query: str
    response: str

class MultiMemoryAgent:
    def __init__(self):
        self.memory_system = MemorySystem()
        self.extractor = StructuredMemoryExtractor()
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def visualize_graph(self, output_path: str = "reports/graph.mermaid"):
        try:
            import os
            if os.path.dirname(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            mermaid_str = self.app.get_graph().draw_mermaid()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(mermaid_str)
            print(f"Graph flow saved to {output_path}")
        except Exception as e:
            print(f"Failed to visualize graph: {e}")

    def _create_workflow(self):
        workflow = StateGraph(MemoryState)
        workflow.add_node("router", self.router_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)
        workflow.add_node("update", self.update_node)
        workflow.set_entry_point("router")
        workflow.add_edge("router", "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "update")
        workflow.add_edge("update", END)
        return workflow

    def router_node(self, state: MemoryState):
        query = state["messages"][-1]["content"]
        return {"current_query": query, "next_node": "retrieve"}

    def retrieve_node(self, state: MemoryState):
        query = state["current_query"]
        targets = self.memory_system.router.route(query)
        results = {}
        if "long-term" in targets:
            results["user_profile"] = self.memory_system.long_term.get_all()
        if "episodic" in targets:
            results["episodes"] = self.memory_system.episodic.retrieve()
        if "semantic" in targets:
            results["semantic_hits"] = self.memory_system.semantic.retrieve(query)
        return results

    def generate_node(self, state: MemoryState):
        profile = state.get("user_profile", {})
        episodes = state.get("episodes", [])
        semantic = state.get("semantic_hits", [])
        prompt = "System: Bạn là trợ lý AI có bộ nhớ đa tầng.\n"
        if profile:
            prompt += f"Thông tin người dùng: {json.dumps(profile, ensure_ascii=False)}\n"
        if episodes:
            prompt += f"Trải nghiệm quá khứ: {json.dumps(episodes, ensure_ascii=False)}\n"
        if semantic:
            prompt += f"Kiến thức liên quan: {', '.join(semantic)}\n"
        query = state["current_query"].lower()
        response = self._mock_llm_response(query, profile, episodes, semantic)
        return {"response": response, "messages": [{"role": "assistant", "content": response}]}

    def update_node(self, state: MemoryState):
        query = state["current_query"]
        facts = self.extractor.extract(query)
        if facts.name: self.memory_system.long_term.save("name", facts.name)
        if facts.allergy: self.memory_system.long_term.save("allergy", facts.allergy)
        if facts.hobby: self.memory_system.long_term.save("hobby", facts.hobby)
        if facts.location: self.memory_system.long_term.save("location", facts.location)
        if any(word in query.lower() for word in ["xong", "hoàn thành", "hoan thanh"]):
            self.memory_system.episodic.save({"task": query, "result": "completed", "timestamp": "2026-04-24"})
        return {}

    def _mock_llm_response(self, query, profile, episodes, semantic):
        if "tôi tên gì" in query or "toi ten gi" in query:
            name = profile.get("name")
            return f"Bạn tên là {name}." if name else "Tôi chưa biết tên bạn."
        if "tôi dị ứng gì" in query or "toi di ung gi" in query:
            allergy = profile.get("allergy")
            return f"Bạn bị dị ứng {allergy}." if allergy else "Tôi không thấy thông tin dị ứng của bạn."
        if "tôi sống ở đâu" in query or "toi song o dau" in query or "toi o dau" in query:
            loc = profile.get("location")
            return f"Bạn sống ở {loc}." if loc else "Tôi chưa biết bạn sống ở đâu."
        if "tên tôi là" in query or "ten toi la" in query:
            prefix = "tên tôi là" if "tên tôi là" in query else "ten toi la"
            name = query.split(prefix)[-1].strip().capitalize()
            return f"Chào {name}! Tôi đã ghi nhớ tên của bạn."
        if "dị ứng" in query or "di ung" in query:
            if any(word in query for word in ["nhầm", "không phải", "nham", "khong phai"]):
                return "Đã hiểu! Tôi đã cập nhật thông tin dị ứng của bạn."
            return "Tôi đã ghi nhận thông tin dị ứng của bạn."
        if "sống ở" in query or "song o" in query:
            if any(word in query for word in ["không", "chuyển", "khong", "chuyen"]):
                return "Đã cập nhật địa chỉ của bạn."
            return "Đã ghi nhận nơi ở của bạn."
        if "docker" in query:
            if semantic:
                return f"Theo tài liệu, service name là '{semantic[0]}'."
            return "Tôi không chắc về service name của Docker."
        if "reset database" in query:
            if semantic:
                return f"Dùng lệnh '{semantic[0]}'."
            return "Tôi không biết lệnh reset database."
        if "lần trước" in query or "quá khứ" in query or "lan truoc" in query or "qua khu" in query:
            if episodes:
                return f"Lần trước bạn đã hoàn thành: {episodes[-1]['task']}."
            return "Tôi chưa thấy trải nghiệm nào trong quá khứ."
        if any(word in query for word in ["môn thể thao", "bóng đá", "mon the thao", "bong da"]):
            hobby = profile.get("hobby")
            if hobby: return f"Bạn thích chơi {hobby}."
            return "Tôi chưa biết sở thích của bạn."
        return "Tôi có thể giúp gì cho bạn?"
