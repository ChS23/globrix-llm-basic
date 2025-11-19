from typing import Annotated
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage
from agent.tools.realty_search import realty_search, RealtyFilter
from agent.tools.regional_rag_tool import regional_rag_tool
from agent.tools.genui_tool import genui_tool

def respond_node(state: MessagesState):
    # Получаем последнее сообщение от пользователя
    last_message = state["messages"][-1].content

    # Нижний регистр для простоты анализа
    user_input = last_message.lower()

    # === Маршрутизация ===
    if any(word in user_input for word in ["недвижимость", "квартира", "дом", "поиск"]):
        # Пример: "найди 2-комнатную квартиру в центре"
        # Пока что — вызываем с фиксированными фильтрами (в будущем можно парсить из сообщения)
        filters = RealtyFilter(rooms=2, location="центр")
        results = realty_search(filters=filters)
        response = f"Найдено {len(results)} объектов недвижимости."
        if results:
            first = results[0]
            response += f"\nНапример: {first['address']}, {first['rooms']} комн., {first['price']} руб."

    elif any(word in user_input for word in ["район", "школа", "инфраструктура", "транспорт"]):
        # Пример: "какие школы рядом с ЖК Солнечный?"
        answer = regional_rag_tool(user_input)
        response = f"Ответ от RAG: {answer}"

    elif any(word in user_input for word in ["лэндинг", "презентация", "сайт"]):
        # Пример: "сделай лэндинг для квартиры"
        # Пока — заглушка, в будущем можно передавать данные
        html = genui_tool({"address": "пр. Космонавтов, 10", "price": 4500000})
        response = "Лэндинг готов (заглушка)"

    else:
        response = "Не понял запрос. Попробуйте: 'найди недвижимость', 'расскажи о районе', 'сделай лэндинг'"

    return {"messages": [AIMessage(content=response)]}

def create_graph(checkpointer: MemorySaver):
    builder = StateGraph(MessagesState)
    builder.add_node("respond", respond_node)
    builder.set_entry_point("respond")
    builder.set_finish_point("respond")
    return builder.compile(checkpointer=checkpointer)