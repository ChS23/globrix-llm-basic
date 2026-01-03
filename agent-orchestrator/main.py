from contextlib import asynccontextmanager
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agent.orchestrator.agent import OrchestratorAgent

# Database URL for checkpointer
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/globrix")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # PostgreSQL connection pool for checkpointer
    # autocommit=True required for CREATE INDEX CONCURRENTLY in setup()
    async with AsyncConnectionPool(
        conninfo=POSTGRES_URL,
        max_size=10,
        min_size=2,
        kwargs={"autocommit": True, "prepare_threshold": 0},
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        print("✅ Checkpoint tables ready")

        agent = OrchestratorAgent(checkpointer=checkpointer)
        app.state.agent = agent
        print("✅ Агент инициализирован (PostgreSQL checkpointer с пулом)")
        yield

    print("🔒 Приложение завершено")

app = FastAPI(
    title="globrix-llm-basic",
    version="0.1.0",
    description="Мультиагентная система для риэлторов: поиск, анализ и презентация недвижимости",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint for Docker/Kubernetes."""
    return {"status": "healthy"}


class ChatRequest(BaseModel):
    thread_id: str = "default"
    deal_id: str | None = None
    message: str = ""

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        thread_id = request.thread_id
        deal_id = request.deal_id or thread_id  # Fallback to thread_id if no deal_id
        user_message = request.message

        # Add deal context to message if deal_id provided
        if request.deal_id:
            context_message = f"[Context: Current deal_id = {deal_id}]\n\n{user_message}"
        else:
            context_message = user_message

        inputs = {"messages": [("user", context_message)]}
        config = {"configurable": {"thread_id": thread_id}}

        output = await app.state.agent.ainvoke(inputs, config)

        last_message = output["messages"][-1]
        return {"response": last_message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка оркестратора: {str(e)}")

# === DEAL STATE API ===
from agent.genui.tools import read_deal_state
from agent.genui.dependencies import get_deal_crud
from services.supabase_client.deal_crud import DealCRUD

@app.get("/api/deal/{deal_id}/state")
async def get_deal_state(
    deal_id: str,
    deal_crud: DealCRUD = Depends(get_deal_crud)
):
    """Get UI state for a deal.

    Returns the current JSON state of the deal page.
    Frontend uses this to render dynamic blocks.
    """
    try:
        state = await read_deal_state(deal_id, deal_crud)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch deal state: {str(e)}")


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