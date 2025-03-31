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
    Upload a sprite file and store its metadata in the database.
    
    In a production environment, the file would be stored in a file storage service
    like AWS S3, and only the metadata would be stored in MongoDB.
    For this assignment, we'll simulate this by storing the file information.
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
    """List all sprites in the database"""
    sprites = await sprites_collection.find().to_list(1000)
    # Convert ObjectId to string for each sprite
    for sprite in sprites:
        sprite["_id"] = str(sprite["_id"])
    return sprites

@router.get("/{id}", response_description="Get a single sprite by ID")
async def get_sprite(id: str):
    """Get a specific sprite by its ID"""
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
    """Delete a sprite by its ID"""
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