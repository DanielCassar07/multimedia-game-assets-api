import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

async def test_connection():
    # Load environment variables
    load_dotenv()
    connection_string = os.getenv("mongodb+srv://danielcassar:1234@game-assets-db.nziy1nm.mongodb.net/?retryWrites=true&w=majority&appName=game-assets-db")
    
    # Attempt to connect
    client = AsyncIOMotorClient(connection_string)
    
    try:
        # Simple operation to verify connection
        server_info = await client.admin.command('ismaster')
        print(" CONNECTION SUCCESSFUL!")
        print(f"Connected to: {server_info.get('me')}")
        print(f"MongoDB version: {server_info.get('version', 'unknown')}")
    except Exception as e:
        print(" CONNECTION FAILED!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())