Lab #17

Mục tiêu: Build Multi-Memory Agent với LangGraph
Deliverable: Agent với full memory stack + benchmark report: so sánh agent có/không memory trên 10 multi-turn conversations.
Thời gian: 2 giờ

Implement 4 memory backends: ConversationBufferMemory (short-term), Redis (long-term), JSON episodic log, Chroma (semantic).

Build memory router: chọn memory type phù hợp dựa trên query intent – user preference vs factual recall vs experience recall.

Context window management: auto-trim khi gần limit, priority-based eviction theo 4-level hierarchy.

Benchmark: so sánh agent có/không memory trên 10 multi-turn conversations – đo response relevance, context utilization, token efficiency.

GitHub repo + benchmark report: bảng so sánh metrics, memory hit rate analysis, token budget breakdown.

Tổng kết – Key Takeaways

Những ý chính cần nhớ sau buổi học hôm nay:

Không có “one size fits all” – production agent cần ít nhất short-term + long-term, thêm episodic/semantic tùy use case.

Memory retrieval quality quyết định agent quality – bad retrieval = irrelevant context = wrong answer.

Memory write-back cần careful design: nhớ gì, khi nào ghi, xử lý conflict ra sao, TTL bao lâu.

Privacy không phải afterthought – GDPR compliance cần thiết kế từ đầu (Privacy-by-Design).