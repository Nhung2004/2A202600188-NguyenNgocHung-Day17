# Benchmark Report - Multi-Memory Agent

| # | Scenario | No-memory result | With-memory result | Pass? |
|---|----------|------------------|---------------------|-------|
| 1 | Recall User Name | Know | Bạn tên là Hung. | Pass |
| 2 | Allergy Conflict Update | Know | Bạn bị dị ứng dau nanh. | Pass |
| 3 | Episodic Recall | Know | Lần trước bạn đã hoàn thành: toi da hoan thanh viec debug docker roi.. | Pass |
| 4 | Semantic Retrieval | Know | Theo tài liệu, service name là 'Docker service name for local development is 'web-app'.'. | Pass |
| 5 | Multi-turn Persistence | Know | Bạn thích chơi bong da. | Pass |
| 6 | Knowledge Recall (DB) | Know | Dùng lệnh 'To reset the database, use 'npm run db:reset'.'. | Pass |
| 7 | Fact Persistence (Restart) | Know | Bạn tên là Hung. | Pass |
| 8 | Location Recall | Know | Bạn sống ở Ha noi. | Pass |
| 9 | Multiple Episodes | Know | Lần trước bạn đã hoàn thành: toi da lam xong bai 2.. | Pass |
| 10 | Complex Update (Location) | Know | Bạn sống ở Sai gon. | Pass |

## Reflection

### 1. Memory nào giúp agent nhất?
Long-term profile giúp agent cá nhân hóa trải nghiệm nhất (nhớ tên, sở thích, dị ứng).

### 2. Memory nào rủi ro nhất nếu retrieve sai?
Semantic memory rủi ro nhất vì có thể đưa ra kiến thức sai lệch hoặc lỗi thời nếu retrieval không chính xác.

### 3. Privacy & Limitations
- **PII Risk**: Lưu trữ tên và thông tin y tế (dị ứng) cần có cơ chế xóa hoặc TTL.
- **Limitation**: Hiện tại agent sử dụng heuristic cho việc router, cần LLM để phân loại intent chính xác hơn khi scale.
