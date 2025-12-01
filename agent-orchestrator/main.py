from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver
from agent.orchestrator.agent import OrchestratorAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    checkpointer = MemorySaver()
    agent = OrchestratorAgent(checkpointer=checkpointer)
    app.state.agent = agent
    print("✅ Агент инициализирован (MemorySaver)")
    yield
    print("🔒 Приложение завершено")

app = FastAPI(
    title="globrix-llm-basic",
    version="0.1.0",
    description="Мультиагентная система для риэлторов: поиск, анализ и презентация недвижимости",
    lifespan=lifespan
)

class ChatRequest(BaseModel):
    thread_id: str = "default"
    message: str = ""

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        thread_id = request.thread_id
        user_message = request.message

        inputs = {"messages": [("user", user_message)]}
        config = {"configurable": {"thread_id": thread_id}}

        output = await app.state.agent.ainvoke(inputs, config)

        last_message = output["messages"][-1]
        return {"response": last_message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка оркестратора: {str(e)}")

# === ТЕСТИРОВАНИЕ ТУЛЗОВ ===
from agent.tools.apartments_search import apartments_search, ApartmentSearchFilter

@app.post("/test-search")
def test_search(filters: ApartmentSearchFilter):
    results = asyncio.run(apartments_search(filters))
    return {"results": results}

@app.get("/test-search-simple")
def test_search_simple():
    from agent.tools.apartments_search import ApartmentSearchFilter
    filters = ApartmentSearchFilter(apartment_type="2br", status="available")
    results = asyncio.run(apartments_search(filters))
    return {"results": results}