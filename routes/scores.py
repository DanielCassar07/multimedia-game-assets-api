from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Optional
from bson import ObjectId
from config import scores_collection
from pydantic import BaseModel, Field
from security import APIKeyHeader
import re

# Get API key dependency
api_key_header = APIKeyHeader()

router = APIRouter(
    prefix="/scores",
    tags=["scores"]
)

class ScoreInput(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=100)
    score: int = Field(..., ge=0)
    game_level: Optional[int] = Field(None, ge=1)
    time_played: Optional[float] = Field(None, ge=0.0)

@router.post("/", response_description="Add a new player score")
async def add_score(score: ScoreInput = Body(...), api_key: str = Depends(api_key_header)):
    """
    Adds a new player score to the database.
    
    Security: Requires API key, validates input with Pydantic model
    
    Database Operation: insert_one() to scores_collection with sanitized data
    Returns the inserted document's ID
    """
    try:
        # Input validation to prevent injection attacks
        if not re.match(r'^[a-zA-Z0-9_]+$', score.player_name):
            raise HTTPException(status_code=400, 
                              detail="Player name can only contain alphanumeric characters and underscores")
        
        # Create score document
        score_data = score.dict()
        
        # Insert into database
        result = await scores_collection.insert_one(score_data)
        
        # Return success response
        return {
            "message": "Player score added successfully",
            "id": str(result.inserted_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add player score: {str(e)}")

@router.get("/", response_description="List all player scores")
async def list_scores():
    """
    Retrieves all player scores from the database.
    
    Database Interaction:
    - Queries scores_collection with find() (no filter)
    - Converts cursor to list (max 1000 documents)
    - Converts ObjectIds to strings for JSON serialization
    """
    scores = await scores_collection.find().to_list(1000)
    # Convert ObjectId to string for each score
    for score in scores:
        score["_id"] = str(score["_id"])
    return scores

@router.get("/top/{limit}", response_description="Get top player scores")
async def get_top_scores(limit: int = 10):
    """
    Retrieves top-scoring players.
    
    Database Interaction:
    - Queries scores_collection with find()
    - Sorts by score in descending order (-1)
    - Limits to specified number of results
    """
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be a positive integer")
        
    scores = await scores_collection.find().sort("score", -1).limit(limit).to_list(limit)
    # Convert ObjectId to string for each score
    for score in scores:
        score["_id"] = str(score["_id"])
    return scores

@router.get("/{id}", response_description="Get a single player score by ID")
async def get_score(id: str):
    """
    Retrieves a specific player score by ID.
    
    Database Interaction:
    - Validates ObjectId format for security
    - Uses find_one() with filter {"_id": ObjectId(id)}
    - Returns 404 if no document found
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
            
        # Get score from database
        if (score := await scores_collection.find_one({"_id": ObjectId(id)})) is not None:
            # Convert ObjectId to string
            score["_id"] = str(score["_id"])
            return score
        raise HTTPException(status_code=404, detail=f"Player score with ID {id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")