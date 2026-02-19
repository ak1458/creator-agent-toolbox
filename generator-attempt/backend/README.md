# Creator Agent Toolbox Backend

## Free Local Development (Ollama)

1. Install Ollama and run it:
   - https://docs.ollama.com/windows
2. Pull a model:
   - `ollama pull llama3.2`
3. Copy env file:
   - `cp .env.example .env`
4. Start API:
   - `python -m uvicorn app.main:app --reload`

Default provider is Ollama (`LLM_PROVIDER=ollama`).

## Switch To OpenAI Later

1. Set env:
   - `LLM_PROVIDER=openai`
   - `OPENAI_API_KEY=...`
2. Restart server.

## API

- Docs: `http://localhost:8000/docs`
- Health: `GET /api/v1/health`
- Start workflow: `POST /api/v1/workflows/start`
