import os
import json
import time
from core.agent import MultiMemoryAgent

class Benchmarker:
    def __init__(self):
        self.agent = MultiMemoryAgent()
        self.scenarios = [
            {
                "id": 1,
                "name": "Recall User Name",
                "turns": [
                    {"role": "user", "content": "Ten toi la Hung."},
                    {"role": "user", "content": "Hom nay thoi tiet the nao?"},
                    {"role": "user", "content": "Toi ten gi?"}
                ],
                "expected": "Hung"
            },
            {
                "id": 2,
                "name": "Allergy Conflict Update",
                "turns": [
                    {"role": "user", "content": "Toi di ung sua bo."},
                    {"role": "user", "content": "A nham, toi di ung dau nanh chu khong phai sua bo."},
                    {"role": "user", "content": "Toi di ung gi?"}
                ],
                "expected": "dau nanh"
            },
            {
                "id": 3,
                "name": "Episodic Recall",
                "turns": [
                    {"role": "user", "content": "Toi da hoan thanh viec debug Docker roi."},
                    {"role": "user", "content": "Lan truoc toi da lam gi?"}
                ],
                "expected": "debug Docker"
            },
            {
                "id": 4,
                "name": "Semantic Retrieval",
                "turns": [
                    {"role": "user", "content": "Docker service name cho local la gi?"}
                ],
                "expected": "web-app"
            },
            {
                "id": 5,
                "name": "Multi-turn Persistence",
                "turns": [
                    {"role": "user", "content": "Toi thich choi bong da."},
                    {"role": "user", "content": "Ban khoe khong?"},
                    {"role": "user", "content": "Toi thich mon the thao nao?"}
                ],
                "expected": "bong da"
            },
            {
                "id": 6,
                "name": "Knowledge Recall (DB)",
                "turns": [
                    {"role": "user", "content": "Lam sao de reset database?"}
                ],
                "expected": "db:reset"
            },
            {
                "id": 7,
                "name": "Fact Persistence (Restart)",
                "turns": [
                    {"role": "user", "content": "Ten toi la Hung."},
                    {"role": "user", "content": "Tam biet."},
                    {"role": "user", "content": "Toi ten gi?"}
                ],
                "expected": "Hung"
            },
            {
                "id": 8,
                "name": "Location Recall",
                "turns": [
                    {"role": "user", "content": "Toi song o Ha Noi."},
                    {"role": "user", "content": "Thoi tiet o do the nao?"},
                    {"role": "user", "content": "Toi song o dau?"}
                ],
                "expected": "Ha Noi"
            },
            {
                "id": 9,
                "name": "Multiple Episodes",
                "turns": [
                    {"role": "user", "content": "Toi da hoc xong bai 1."},
                    {"role": "user", "content": "Toi da lam xong bai 2."},
                    {"role": "user", "content": "Lan truoc toi da lam gi?"}
                ],
                "expected": "bai 2"
            },
            {
                "id": 10,
                "name": "Complex Update (Location)",
                "turns": [
                    {"role": "user", "content": "Toi song o Ha Noi."},
                    {"role": "user", "content": "A khong, toi da chuyen vao Sai Gon roi."},
                    {"role": "user", "content": "Hien tai toi o dau?"}
                ],
                "expected": "Sai Gon"
            }
        ]

    def run_benchmark(self):
        results = []
        print(f"{'#':<3} | {'Scenario':<25} | {'No-Memory':<15} | {'With-Memory':<15} | {'Pass?'}")
        print("-" * 70)
        
        # Ensure data and reports directories exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        
        for scene in self.scenarios:
            # Cleanup previous data
            if os.path.exists("data/profile.json"): os.remove("data/profile.json")
            if os.path.exists("data/episodes.jsonl"): os.remove("data/episodes.jsonl")
            
            # 1. No-memory run
            no_mem_agent = MultiMemoryAgent()
            no_mem_state = {"messages": [], "user_profile": {}, "episodes": [], "semantic_hits": [], "response": "", "current_query": ""}
            no_mem_res = ""
            for turn in scene["turns"]:
                no_mem_state["messages"] = [turn]
                no_mem_state = no_mem_agent.app.invoke(no_mem_state)
                no_mem_res = no_mem_state["response"]
            no_mem_passed = scene["expected"].lower() in no_mem_res.lower()
            
            # 2. With-memory run
            with_mem_agent = MultiMemoryAgent()
            with_mem_state = {"messages": [], "user_profile": {}, "episodes": [], "semantic_hits": [], "response": "", "current_query": ""}
            with_mem_res = ""
            for turn in scene["turns"]:
                with_mem_state["messages"] = [turn]
                with_mem_state = with_mem_agent.app.invoke(with_mem_state)
                with_mem_res = with_mem_state["response"]
            
            with_mem_passed = scene["expected"].lower() in with_mem_res.lower()
            status = "PASS" if with_mem_passed else "FAIL"
            
            results.append({
                "id": scene["id"],
                "name": scene["name"],
                "no_mem": "Know" if no_mem_passed else "Unknown",
                "with_mem": with_mem_res,
                "pass": with_mem_passed
            })
            
            print(f"Scenario {scene['id']}: {status}")
            
        self._generate_report(results)

    def _generate_report(self, results):
        os.makedirs("reports", exist_ok=True)
        # 1. Export to Markdown
        with open("reports/BENCHMARK.md", "w", encoding="utf-8") as f:
            # ... (markdown logic remains)
            f.write("# Benchmark Report - Multi-Memory Agent\n\n")
            f.write("| # | Scenario | No-memory result | With-memory result | Pass? |\n")
            f.write("|---|----------|------------------|---------------------|-------|\n")
            for r in results:
                f.write(f"| {r['id']} | {r['name']} | {r['no_mem']} | {r['with_mem']} | {'Pass' if r['pass'] else 'Fail'} |\n")
            
            f.write("\n## Reflection\n\n")
            f.write("### 1. Memory nào giúp agent nhất?\n")
            f.write("Long-term profile giúp agent cá nhân hóa trải nghiệm nhất (nhớ tên, sở thích, dị ứng).\n\n")
            f.write("### 2. Memory nào rủi ro nhất nếu retrieve sai?\n")
            f.write("Semantic memory rủi ro nhất vì có thể đưa ra kiến thức sai lệch hoặc lỗi thời nếu retrieval không chính xác.\n\n")
            f.write("### 3. Privacy & Limitations\n")
            f.write("- **PII Risk**: Lưu trữ tên và thông tin y tế (dị ứng) cần có cơ chế xóa hoặc TTL.\n")
            f.write("- **Limitation**: Hiện tại agent sử dụng heuristic cho việc router, cần LLM để phân loại intent chính xác hơn khi scale.\n")

        # 2. Export to JSON (Yeu cau nop bai)
        with open("reports/benchmark_conversation.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nDa xuat bao cao chi tiet ra reports/benchmark_conversation.json")

if __name__ == "__main__":
    bench = Benchmarker()
    bench.run_benchmark()
