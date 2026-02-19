# Creator Agent Toolbox 🚀

A comprehensive suite of AI-powered tools for content creators, designed to streamline video production workflows from trend analysis to multivariant A/B testing.

## 🏗️ Architecture

- **Backend**: FastAPI paired with LangGraph for complex agentic workflows.
- **AI Engine**: Groq (Llama-3-70b-versatile via OpenAI compatibility) for rapid script generation.
- **Frontend**: React + Vite + Tailwind CSS for a premium, responsive dashboard.
- **Database**: SQLModel with a persistent SQLite disk for stateless deployment stability.

## 🌟 Key Features

### 1. Agentic Workflow Engine

An automated pipeline that coordinates multiple specialized agents:

- **Trend Analyst**: Scours niches for high-performing content patterns.
- **Script Architect**: Drafts 3 distinct script variants based on viral structures.
- **Visual Engineer**: Generates high-conversion thumbnail prompts.

### 2. Multi-Variant A/B Testing

Live monitoring of content performance variants with automated winner declaration or manual override.

### 3. Workflow Persistence

Stateful checkpointer allows pausing and resuming long-running creative processes.

## 🚀 Deployment

### Backend (Render)

- **Runtime**: Python 3.11
- **Disk**: 1GB persistent disk mounted at `/opt/render/project/src/data`
- **LLM**: Powered by Groq for ultra-low latency generation.

### Frontend (Vercel)

- Automated CI/CD deployments from the `frontend` root directory.
- Dynamic API client routing for cross-origin production requests.

---

## 📈 Future Scaling Roadmap

- **Vector Database Integration**: Move from SQLite to Pinecone or PGVector for RAG-based content memory.
- **Distributed Caching**: Implement Redis (upgradable from current local-first cache) for high-traffic script retrieval.
- **Multi-Platform Adapters**: Expand from YouTube-centric logic to Instagram Reels, TikTok, and LinkedIn.
- **User Authentication**: Implement OAuth2 support for team-based workspaces.

---

*Built withsenior developer standards for high performance and scalability.*
