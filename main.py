from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from bson import ObjectId
from typing import Optional
import json
from datetime import datetime

from database import parcels_collection, albums_collection
from models import Parcel, Album

app = FastAPI(title="Delivery & Music Database System")
templates = Jinja2Templates(directory="templates")


# Вспомогательная функция для конвертации ObjectId
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ============= ГЛАВНАЯ СТРАНИЦА =============
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ============= API ДЛЯ ПОСЫЛОК (PARCELS) =============

@app.get("/api/parcels")
async def get_parcels(
        status: Optional[str] = None,
        courier: Optional[str] = None,
        min_weight: Optional[float] = None
):
    """Получить список всех посылок с фильтрацией"""
    query = {}

    if status:
        query["status"] = status
    if courier:
        query["courier.full_name"] = {"$regex": courier, "$options": "i"}
    if min_weight:
        query["parcel_info.weight_kg"] = {"$gte": min_weight}

    parcels = list(parcels_collection.find(query))
    return [serialize_doc(p) for p in parcels]


@app.get("/api/parcels/{parcel_id}")
async def get_parcel(parcel_id: str):
    """Получить одну посылку по ID"""
    try:
        parcel = parcels_collection.find_one({"_id": ObjectId(parcel_id)})
        if not parcel:
            raise HTTPException(status_code=404, detail="Посылка не найдена")
        return serialize_doc(parcel)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/parcels")
async def create_parcel(parcel: Parcel):
    """Создать новую посылку"""
    parcel_dict = parcel.model_dump()
    result = parcels_collection.insert_one(parcel_dict)
    return {"id": str(result.inserted_id), "message": "Посылка успешно создана"}


@app.put("/api/parcels/{parcel_id}")
async def update_parcel(parcel_id: str, parcel: Parcel):
    """Обновить посылку"""
    try:
        parcel_dict = parcel.model_dump()
        result = parcels_collection.update_one(
            {"_id": ObjectId(parcel_id)},
            {"$set": parcel_dict}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Посылка не найдена")
        return {"message": "Посылка успешно обновлена"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/parcels/{parcel_id}")
async def delete_parcel(parcel_id: str):
    """Удалить посылку"""
    try:
        result = parcels_collection.delete_one({"_id": ObjectId(parcel_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Посылка не найдена")
        return {"message": "Посылка успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= API ДЛЯ АЛЬБОМОВ (ALBUMS) =============

@app.get("/api/albums")
async def get_albums(
        artist: Optional[str] = None,
        genre: Optional[str] = None,
        min_rating: Optional[float] = None
):
    """Получить список всех альбомов с фильтрацией"""
    query = {}

    if artist:
        query["artist"] = {"$regex": artist, "$options": "i"}
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}
    if min_rating:
        query["rating"] = {"$gte": min_rating}

    albums = list(albums_collection.find(query))
    return [serialize_doc(a) for a in albums]


@app.get("/api/albums/{album_id}")
async def get_album(album_id: str):
    """Получить один альбом по ID"""
    try:
        album = albums_collection.find_one({"_id": ObjectId(album_id)})
        if not album:
            raise HTTPException(status_code=404, detail="Альбом не найден")
        return serialize_doc(album)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/albums")
async def create_album(album: Album):
    """Создать новый альбом"""
    album_dict = album.model_dump()
    result = albums_collection.insert_one(album_dict)
    return {"id": str(result.inserted_id), "message": "Альбом успешно создан"}


@app.put("/api/albums/{album_id}")
async def update_album(album_id: str, album: Album):
    """Обновить альбом"""
    try:
        album_dict = album.model_dump()
        result = albums_collection.update_one(
            {"_id": ObjectId(album_id)},
            {"$set": album_dict}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Альбом не найден")
        return {"message": "Альбом успешно обновлен"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/albums/{album_id}")
async def delete_album(album_id: str):
    """Удалить альбом"""
    try:
        result = albums_collection.delete_one({"_id": ObjectId(album_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Альбом не найден")
        return {"message": "Альбом успешно удален"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= ОТЧЕТЫ =============

@app.get("/api/reports/parcels-by-status")
async def report_parcels_by_status():
    """Отчет: Посылки сгруппированные по статусу"""
    pipeline = [
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total_weight": {"$sum": "$parcel_info.weight_kg"}
        }},
        {"$sort": {"count": -1}}
    ]
    result = list(parcels_collection.aggregate(pipeline))
    return result


@app.get("/api/reports/albums-by-genre")
async def report_albums_by_genre():
    """Отчет: Альбомы сгруппированные по жанру"""
    pipeline = [
        {"$group": {
            "_id": "$genre",
            "count": {"$sum": 1},
            "avg_rating": {"$avg": "$rating"}
        }},
        {"$sort": {"count": -1}}
    ]
    result = list(albums_collection.aggregate(pipeline))
    return result


@app.get("/api/reports/couriers-workload")
async def report_couriers_workload():
    """Отчет: Загруженность курьеров"""
    pipeline = [
        {"$group": {
            "_id": "$courier.full_name",
            "total_deliveries": {"$sum": 1},
            "total_weight": {"$sum": "$parcel_info.weight_kg"}
        }},
        {"$sort": {"total_deliveries": -1}}
    ]
    result = list(parcels_collection.aggregate(pipeline))
    return result


# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)