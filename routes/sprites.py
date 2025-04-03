from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
from bson import ObjectId
from config import sprites_collection
from security import APIKeyHeader
import re

# Get API key dependency
api_key_header = APIKeyHeader()

router = APIRouter(
    prefix="/sprites",
    tags=["sprites"]
)

@router.post("/", response_description="Upload a new sprite")
async def upload_sprite(file: UploadFile = File(...), api_key: str = Depends(api_key_header)):
    """
    Uploads a sprite file and stores its metadata in the database.
    
    Security: Requires API key, validates filename pattern to prevent injection
    
    Database Operation: insert_one() to sprites_collection
    Returns the inserted document's ID and metadata
    """
    try:
        # Read file content (in production, you'd upload to S3 or similar)
        content = await file.read()
        file_size = len(content)
        
        # Validate file name for security
        if not re.match(r'^[a-zA-Z0-9_\-\.]+\.(png|jpg|jpeg|gif)$', file.filename):
            raise HTTPException(status_code=400, 
                                detail="Invalid filename. Use only letters, numbers, underscores, hyphens, and valid image extensions.")
        
        # Extract file extension
        file_extension = file.filename.split(".")[-1].lower()
        
        # Create a sprite document
        sprite_data = {
            "name": file.filename.split(".")[0],
            "file_path": f"/assets/sprites/{file.filename}",
            "width": 64,  # Default values for demo
            "height": 64,  # Default values for demo
            "format": file_extension,
            "tags": ["uploaded", file_extension],
            "description": f"Uploaded sprite: {file.filename}"
        }
        
        # Insert into database
        result = await sprites_collection.insert_one(sprite_data)
        
        # Return success response
        return {
            "message": "Sprite uploaded successfully",
            "id": str(result.inserted_id),
            "filename": file.filename,
            "size": file_size,
            "format": file_extension
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload sprite: {str(e)}")

@router.get("/", response_description="List all sprites")
async def list_sprites():
    """
    Retrieves all sprite assets from the database.
    
    Database Interaction:
    - Queries sprites_collection with find() (no filter)
    - Converts cursor to list (max 1000 documents)
    - Converts ObjectIds to strings for JSON serialization
    """
    sprites = await sprites_collection.find().to_list(1000)
    # Convert ObjectId to string for each sprite
    for sprite in sprites:
        sprite["_id"] = str(sprite["_id"])
    return sprites

@router.get("/{id}", response_description="Get a single sprite by ID")
async def get_sprite(id: str):
    """
    Retrieves a specific sprite by ID.
    
    Database Interaction:
    - Validates ObjectId format for security
    - Uses find_one() with filter {"_id": ObjectId(id)}
    - Returns 404 if no document found
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
            
        # Get sprite from database
        if (sprite := await sprites_collection.find_one({"_id": ObjectId(id)})) is not None:
            # Convert ObjectId to string
            sprite["_id"] = str(sprite["_id"])
            return sprite
        raise HTTPException(status_code=404, detail=f"Sprite with ID {id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/{id}", response_description="Delete a sprite")
async def delete_sprite(id: str, api_key: str = Depends(api_key_header)):
    """
    Deletes a sprite by its ID.
    
    Security: Requires API key, validates ID format
    
    Database Operation: 
    - Uses delete_one() with filter {"_id": ObjectId(id)}
    - Verifies deletion by checking deleted_count
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
            
        # Delete from database
        delete_result = await sprites_collection.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            return {"message": f"Sprite with ID {id} deleted successfully"}
        raise HTTPException(status_code=404, detail=f"Sprite with ID {id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")