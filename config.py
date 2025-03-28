import os
from dotenv import load_dotenv
import motor.motor_asyncio

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")

# Create async client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)

# Get database
db = client.multimedia_game_assets

# Define collections
sprites_collection = db.sprites
audio_collection = db.audio
scores_collection = db.scores