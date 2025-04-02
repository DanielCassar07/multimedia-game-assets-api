from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
        
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SpriteModel(MongoBaseModel):
    name: str = Field(..., min_length=1, max_length=100, regex="^[a-zA-Z0-9_\\-\\.]+$")
    file_path: str
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)
    format: str = Field(..., regex="^(png|jpg|jpeg|gif)$")
    tags: List[str] = []
    description: Optional[str] = None

class AudioModel(MongoBaseModel):
    name: str = Field(..., min_length=1, max_length=100, regex="^[a-zA-Z0-9_\\-\\.]+$")
    file_path: str
    duration: float = Field(..., ge=0.0)
    format: str = Field(..., regex="^(mp3|wav|ogg)$")
    tags: List[str] = []
    description: Optional[str] = None

class PlayerScoreModel(MongoBaseModel):
    player_name: str = Field(..., min_length=1, max_length=100, regex="^[a-zA-Z0-9_]+$")
    score: int = Field(..., ge=0)  # Must be greater than or equal to 0
    game_level: Optional[int] = Field(None, ge=1)  # Must be greater than or equal to 1
    time_played: Optional[float] = Field(None, ge=0.0)  # Must be non-negative

class ScoreInput(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=100)
    score: int = Field(..., ge=0)
    game_level: Optional[int] = Field(None, ge=1)
    time_played: Optional[float] = Field(None, ge=0.0)