from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from memory_system import MemorySystem
import operator

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
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

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
        # In a real app, this would be an LLM call to classify intent
        targets = self.memory_system.router.route(query)
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
        # Construct dynamic prompt
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
            
        # Simulating LLM response based on memory
        query = state["current_query"].lower()
        response = self._mock_llm_response(query, profile, episodes, semantic)
        
        return {"response": response, "messages": [{"role": "assistant", "content": response}]}

    def update_node(self, state: MemoryState):
        query = state["current_query"].lower()
        response = state["response"]
        
        # Simple extraction logic (In real life, use LLM)
        if "tên tôi là" in query or "ten toi la" in query:
            prefix = "tên tôi là" if "tên tôi là" in query else "ten toi la"
            name = query.split(prefix)[-1].strip().strip(".,!?").capitalize()
            self.memory_system.long_term.save("name", name)
            
        if "dị ứng" in query or "di ung" in query:
            prefix = "dị ứng" if "dị ứng" in query else "di ung"
            if "không phải" in query or "nhầm" in query or "khong phai" in query or "nham" in query:
                parts = query.split(prefix)
                if len(parts) > 1:
                    new_allergy = parts[1].split("chứ không phải")[0].split("chu khong phai")[0].strip().strip(".,!?")
                    self.memory_system.long_term.save("allergy", new_allergy)
            else:
                allergy = query.split(prefix)[-1].strip().strip(".,!?")
                self.memory_system.long_term.save("allergy", allergy)
        
        if "thích" in query or "thich" in query and ("chơi" in query or "choi" in query):
            prefix = "chơi" if "chơi" in query else "choi"
            hobby = query.split(prefix)[-1].strip().strip(".,!?")
            self.memory_system.long_term.save("hobby", hobby)

        if any(word in query for word in ["sống ở", "song o", "chuyển", "chuyen"]):
            if any(word in query for word in ["không,", "chuyển", "khong,", "chuyen"]):
                # Case: "chuyển vào [Location] rồi" or "chuyen vao [Location] roi"
                temp = query
                for marker in ["vào", "vao"]:
                    if marker in temp:
                        temp = temp.split(marker)[-1]
                for marker in ["rồi", "roi"]:
                    if marker in temp:
                        temp = temp.split(marker)[0]
                loc = temp.strip().strip(".,!?")
                self.memory_system.long_term.save("location", loc.capitalize())
            else:
                prefix = ""
                for p in ["sống ở", "song o"]:
                    if p in query: prefix = p; break
                if prefix:
                    loc = query.split(prefix)[-1].strip().strip(".,!?")
                    self.memory_system.long_term.save("location", loc.capitalize())

        # Save episodic memory for completed tasks
        if any(word in query for word in ["xong", "hoàn thành", "hoan thanh"]):
            self.memory_system.episodic.save({"task": query, "result": "completed", "timestamp": "2026-04-24"})

        return {}

    def _mock_llm_response(self, query, profile, episodes, semantic):
        # Heuristics for the 10 scenarios - SPECIFIC FIRST
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

import json # For prompt construction
