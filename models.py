from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Модели для посылок
class PassportData(BaseModel):
    series: str
    number: str
    issued_by: str
    issue_date: str

class PersonInfo(BaseModel):
    full_name: str
    address: str
    passport: PassportData

class Dimensions(BaseModel):
    length_cm: float
    width_cm: float
    height_cm: float

class ParcelInfo(BaseModel):
    weight_kg: float
    dimensions: Dimensions
    description: str

class CourierInfo(BaseModel):
    full_name: str
    phone: str
    vehicle: str

class Dates(BaseModel):
    sent_date: str
    delivered_date: Optional[str] = None

class Parcel(BaseModel):
    sender: PersonInfo
    recipient: PersonInfo
    parcel_info: ParcelInfo
    courier: CourierInfo
    dates: Dates
    status: str = "pending"
    tracking_number: str

# Модели для альбомов
class Track(BaseModel):
    number: int
    title: str
    duration: str

class Album(BaseModel):
    title: str
    artist: str
    release_date: str
    genre: str
    label: str
    tracks: List[Track]
    total_duration: str
    rating: float
    sales_millions: Optional[float] = None
    format: List[str]
    country: str