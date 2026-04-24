from core.agent import MultiMemoryAgent
import os
import json
import sys

# Thiet lap stdout de ho tro UTF-8 neu co the
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

def main():
    # Dam bao thu muc data va reports ton tai
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Xoa bo nho cu de bat dau sach
    if os.path.exists("data/profile.json"): os.remove("data/profile.json")
    if os.path.exists("data/episodes.jsonl"): os.remove("data/episodes.jsonl")
    
    # Khoi tao Agent
    print("--- Khoi tao Multi-Memory Agent (LangGraph) ---")
    agent = MultiMemoryAgent()
    
    # Bonus: Visualize Graph Flow
    agent.visualize_graph("reports/graph.mermaid")
    
    # Demo hoi thoai de nap du lieu vao Profile
    print("\n--- Demo: Nap du lieu vao Long-term Memory ---")
    demo_turns = [
        "Ten toi la Hung.",
        "Toi thich choi bong da.",
        "Toi song o Ha Noi."
    ]
    
    state = {"messages": [], "user_profile": {}, "episodes": [], "semantic_hits": [], "response": "", "current_query": ""}
    
    for turn in demo_turns:
        try:
            print(f"User: {turn}")
        except:
            print(f"User: [Input contains special characters]")
            
        state["messages"] = [{"role": "user", "content": turn}]
        state = agent.app.invoke(state)
        
        try:
            print(f"Agent: {state['response']}")
        except:
            # Fallback for encoding issues in terminal
            clean_res = state['response'].encode('ascii', 'ignore').decode()
            print(f"Agent (ASCII): {clean_res}")
    
    # Kiem tra Token Count (Bonus)
    tokens = agent.memory_system.short_term.get_total_tokens()
    print(f"\n[Bonus] Tong so tokens trong Short-term memory: {tokens}")
    
    # Kiem tra file profile.json
    print("\n--- Kiem tra file data/profile.json ---")
    if os.path.exists("data/profile.json"):
        with open("data/profile.json", "r", encoding="utf-8") as f:
            print(json.dumps(json.load(f), indent=2))
            
    print("\n--- HOAN TAT DEMO ---")
    print("1. Kiem tra 'data/profile.json' de xem du lieu ben vung.")
    print("2. Kiem tra 'reports/graph.mermaid' de xem so do luong LangGraph.")
    print("3. Chay 'python benchmark.py' de xem bao cao danh gia trong 'reports/'.")

if __name__ == "__main__":
    main()
