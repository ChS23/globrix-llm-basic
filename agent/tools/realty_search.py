from typing import List, Dict, Optional
from pydantic import BaseModel

# Пример базы данных объектов недвижимости (в реальности — из CSV/SQL/JSON)
REALTY_DB = [
    {
        "id": 1,
        "address": "пр. Космонавтов, 10",
        "rooms": 2,
        "area": 50.5,
        "price": 4500000,
        "location": "центр",
        "has_parking": True,
        "has_balcony": True,
        "description": "Уютная квартира в центре, рядом парк и школы.",
        "image_url": "https://example.com/image1.jpg",
        "transport": "Остановка в 2 минутах",
        "infrastructure": ["школа", "садик", "аптека"]
    },
    {
        "id": 2,
        "address": "ул. Морская, 5",
        "rooms": 3,
        "area": 80.0,
        "price": 7200000,
        "location": "прибрежный",
        "has_parking": False,
        "has_balcony": True,
        "description": "Вид на море, тихий двор.",
        "image_url": "https://example.com/image2.jpg",
        "transport": "Автобус до центра каждые 15 мин",
        "infrastructure": ["пляж", "кафе", "парк"]
    },
    {
        "id": 3,
        "address": "ул. Ленина, 25",
        "rooms": 1,
        "area": 35.0,
        "price": 3200000,
        "location": "новостройка",
        "has_parking": True,
        "has_balcony": False,
        "description": "Современная студия в новом ЖК.",
        "image_url": "https://example.com/image3.jpg",
        "transport": "Скоро будет остановка",
        "infrastructure": ["детсад", "магазин", "аптека"]
    },
    {
        "id": 4,
        "address": "ул. Азовская, 12",
        "rooms": 4,
        "area": 120.0,
        "price": 12000000,
        "location": "частный сектор",
        "has_parking": True,
        "has_balcony": True,
        "description": "Дом с участком, рядом лес.",
        "image_url": "https://example.com/image4.jpg",
        "transport": "Своя парковка",
        "infrastructure": ["школа", "магазин", "остановка"]
    },
    {
        "id": 5,
        "address": "пр. Мира, 45",
        "rooms": 2,
        "area": 60.0,
        "price": 5500000,
        "location": "спальный район",
        "has_parking": False,
        "has_balcony": True,
        "description": "Квартира в тихом районе, рядом школа.",
        "image_url": "https://example.com/image5.jpg",
        "transport": "Остановка в 5 минутах",
        "infrastructure": ["школа", "садик", "магазин"]
    },
]

class RealtyFilter(BaseModel):
    rooms: Optional[int] = None
    location: Optional[str] = None
    has_parking: Optional[bool] = None
    has_balcony: Optional[bool] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    area_min: Optional[float] = None
    area_max: Optional[float] = None

def realty_search(
    query: str = "",
    filters: Optional[RealtyFilter] = None
) -> List[Dict]:
    """
    Ищет объекты недвижимости по заданным фильтрам и/или текстовому запросу.

    Args:
        query: текстовый запрос (например, "квартира с видом на море")
        filters: фильтры (rooms, location, price_min/max и т.д.)

    Returns:
        Список объектов недвижимости, подходящих под критерии
    """
    if filters is None:
        filters = RealtyFilter()

    # Начинаем с полной базы
    results = REALTY_DB

    # Применяем фильтры
    if filters.rooms is not None:
        results = [r for r in results if r["rooms"] == filters.rooms]
    if filters.location:
        results = [r for r in results if filters.location.lower() in r["location"].lower()]
    if filters.has_parking is not None:
        results = [r for r in results if r["has_parking"] == filters.has_parking]
    if filters.has_balcony is not None:
        results = [r for r in results if r["has_balcony"] == filters.has_balcony]
    if filters.price_min is not None:
        results = [r for r in results if r["price"] >= filters.price_min]
    if filters.price_max is not None:
        results = [r for r in results if r["price"] <= filters.price_max]
    if filters.area_min is not None:
        results = [r for r in results if r["area"] >= filters.area_min]
    if filters.area_max is not None:
        results = [r for r in results if r["area"] <= filters.area_max]

    # Пока без семантического поиска по query (добавить позже)
    # if query:
    #     results = [r for r in results if query.lower() in r["description"].lower()]

    return results[:10]  # возвращаем топ-10 результатов
