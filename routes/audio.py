from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
from bson import ObjectId
from config import audio_collection
from security import APIKeyHeader
import re

# Get API key dependency
api_key_header = APIKeyHeader()

router = APIRouter(
    prefix="/audio",
    tags=["audio"]
)

@router.post("/", response_description="Upload a new audio file")
async def upload_audio(file: UploadFile = File(...), api_key: str = Depends(api_key_header)):
    """
    Uploads an audio file and stores its metadata.
    
    Security: Requires API key, validates file extension
    
    Database Operation: insert_one() to audio_collection
    Returns the inserted document's ID and metadata
    """
    try:
        # Read file content (in production, you'd upload to S3 or similar)
        content = await file.read()
        file_size = len(content)
        
        # Validate file name for security
        if not re.match(r'^[a-zA-Z0-9_\-\.]+\.(mp3|wav|ogg)$', file.filename):
            raise HTTPException(status_code=400, 
                                detail="Invalid filename. Use only letters, numbers, underscores, hyphens, and valid audio extensions.")
        
        # Extract file extension
        file_extension = file.filename.split(".")[-1].lower()
        
        # Create an audio document
        audio_data = {
            "name": file.filename.split(".")[0],
            "file_path": f"/assets/audio/{file.filename}",
            "duration": 0.0,  # Would be extracted from the actual file in production
            "format": file_extension,
            "tags": ["uploaded", file_extension],
            "description": f"Uploaded audio: {file.filename}"
        }
        
        # Insert into database
        result = await audio_collection.insert_one(audio_data)
        
        # Return success response
        return {
            "message": "Audio file uploaded successfully",
            "id": str(result.inserted_id),
            "filename": file.filename,
            "size": file_size,
            "format": file_extension
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload audio file: {str(e)}")

@router.get("/", response_description="List all audio files")
async def list_audio_files():
    """
    Retrieves all audio assets from the database.
    
    Database Interaction:
    - Queries audio_collection with find() (no filter)
    - Converts cursor to list (max 1000 documents)
    - Converts ObjectIds to strings for JSON serialization
    """
    audio_files = await audio_collection.find().to_list(1000)
    # Convert ObjectId to string for each audio file
    for audio in audio_files:
        audio["_id"] = str(audio["_id"])
    return audio_files

@router.get("/{id}", response_description="Get a single audio file by ID")
async def get_audio_file(id: str):
    """
    Retrieves a specific audio file by ID.
    
    Database Interaction:
    - Validates ObjectId format for security
    - Uses find_one() with filter {"_id": ObjectId(id)}
    - Returns 404 if no document found
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid ID format")
            
        # Get audio from database
        if (audio := await audio_collection.find_one({"_id": ObjectId(id)})) is not None:
            # Convert ObjectId to string
            audio["_id"] = str(audio["_id"])
            return audio
        raise HTTPException(status_code=404, detail=f"Audio file with ID {id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/{id}", response_description="Delete an audio file")
async def delete_audio_file(id: str, api_key: str = Depends(api_key_header)):
    """
    Deletes an audio file by its ID.
    
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
        delete_result = await audio_collection.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 1:
            return {"message": f"Audio file with ID {id} deleted successfully"}
        raise HTTPException(status_code=404, detail=f"Audio file with ID {id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")