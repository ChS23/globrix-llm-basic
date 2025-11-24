from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver  # ← временно
from agent.orchestrator.agent import OrchestratorAgent

# Управление жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Временно используем MemorySaver
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

        # Асинхронный вызов графа через агент
        output = await app.state.agent.ainvoke(inputs, config)

        # Возвращаем последнее сообщение ассистента
        last_message = output["messages"][-1]
        return {"response": last_message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка оркестратора: {str(e)}")

# === ТЕСТИРОВАНИЕ ТУЛЗОВ ===
from agent.tools.realty_search import realty_search, RealtyFilter

@app.post("/test-search")
def test_search(filters: RealtyFilter):
    results = realty_search(filters=filters)
    return {"results": results}

@app.get("/test-search-simple")
def test_search_simple():
    from agent.tools.realty_search import RealtyFilter
    filters = RealtyFilter(rooms=2, location="центр")
    results = realty_search(filters=filters)
    return {"results": results}