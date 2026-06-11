AI Customer Support Assistant

• Single page HTML only FrontEnd (Chat UI with streaming), and  Python Backend
• Backend connects to: SQLite (users, metadata), ChromaDB (vector search)
• Use local LLM (Gemma4 2b on llama.cpp), and OpenRouter Free API as alternative 
• Use lightLLM to switch between local and cloud LLMs
• LLM for response generation, Redis for caching frequent queries
• Flow: User asks → Backend retrieves relevant docs from ChromaDB → Augments prompt
• → Sends to LLM → Streams response back to user with source citations
• Result: Accurate, verifiable, domain-specific answers grounded in company data• Deploy everything local in one repo (no Docker)

