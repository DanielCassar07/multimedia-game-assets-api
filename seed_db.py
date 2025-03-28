import asyncio
from datetime import datetime
from config import db

async def seed_database():
    # Clear existing collections
    await db.sprites.delete_many({})
    await db.audio.delete_many({})
    await db.scores.delete_many({})
    
    # Sample sprite data
    sprite_data = [
        {
            "name": "player_idle",
            "file_path": "/assets/sprites/player_idle.png",
            "width": 64,
            "height": 64,
            "format": "png",
            "tags": ["player", "character", "idle"],
            "description": "Player character in idle position",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "player_run",
            "file_path": "/assets/sprites/player_run.png",
            "width": 64,
            "height": 64,
            "format": "png",
            "tags": ["player", "character", "running"],
            "description": "Player character running animation",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "enemy_basic",
            "file_path": "/assets/sprites/enemy_basic.png",
            "width": 48,
            "height": 48,
            "format": "png",
            "tags": ["enemy", "character"],
            "description": "Basic enemy character",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    # Sample audio data
    audio_data = [
        {
            "name": "background_music",
            "file_path": "/assets/audio/background_music.mp3",
            "duration": 120.5,
            "format": "mp3",
            "tags": ["music", "background", "loop"],
            "description": "Main background music loop",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "jump_sound",
            "file_path": "/assets/audio/jump_sound.wav",
            "duration": 0.8,
            "format": "wav",
            "tags": ["sfx", "player", "jump"],
            "description": "Sound effect for player jumping",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "collect_item",
            "file_path": "/assets/audio/collect_item.wav",
            "duration": 0.5,
            "format": "wav",
            "tags": ["sfx", "item", "collect"],
            "description": "Sound effect for collecting items",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    # Sample player score data
    score_data = [
        {
            "player_name": "Player1",
            "score": 1500,
            "game_level": 3,
            "time_played": 1200.5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "player_name": "Player2",
            "score": 2800,
            "game_level": 5,
            "time_played": 1800.2,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "player_name": "Player3",
            "score": 950,
            "game_level": 2,
            "time_played": 600.0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    # Insert data into collections
    await db.sprites.insert_many(sprite_data)
    await db.audio.insert_many(audio_data)
    await db.scores.insert_many(score_data)
    
    print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_database())