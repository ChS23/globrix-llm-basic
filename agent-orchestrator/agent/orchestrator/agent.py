import asyncio
from typing import Annotated
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage
from agent.tools.apartments_search import apartments_search, ApartmentSearchFilter
from agent.tools.genui_tool import genui_tool
from agent.tools.regional_rag_tool import regional_rag_tool

class OrchestratorAgent:
    def __init__(self, checkpointer: MemorySaver):
        self.checkpointer = checkpointer
        self.graph = self.create_graph()

    async def create_node(self, state: MessagesState):
        last_message = state["messages"][-1].content
        user_input = last_message.lower()

        # === Маршрутизация ===
        if any(word in user_input for word in ["недвижимость", "квартира", "дом", "поиск", "апартаменты"]):
            filters = ApartmentSearchFilter(apartment_type="2br", status="available")
            results = await apartments_search(filters)
            response = f"Найдено {len(results)} апартаментов."
            if results:
                first = results[0]
                response += f"\nНапример: {first.get('type', 'Тип не указан')}, {first.get('area', '0')} кв.м, {first.get('price', 'Цена не указана')}."

        elif any(word in user_input for word in ["район", "школа", "инфраструктура", "транспорт"]):
            answer = regional_rag_tool(user_input)
            response = f"Ответ от RAG: {answer}"

        elif any(word in user_input for word in ["лэндинг", "презентация", "сайт"]):
            html = await genui_tool({"project_id": "123"})
            response = "Лэндинг готов (заглушка)."

        else:
            response = "Не понял запрос. Попробуйте: 'найди апартаменты', 'расскажи о районе', 'сделай лэндинг'."

        return {"messages": [AIMessage(content=response)]}

    def create_graph(self):
        builder = StateGraph(MessagesState)
        builder.add_node("respond", self.create_node)
        builder.set_entry_point("respond")
        builder.set_finish_point("respond")
        return builder.compile(checkpointer=self.checkpointer)

    async def ainvoke(self, inputs: dict, config: dict):
        return await self.graph.ainvoke(inputs, config)