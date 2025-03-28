# Multimedia Game Assets API

A RESTful API for managing game assets including sprites, audio files, and player scores using FastAPI and MongoDB Atlas.

## Technologies Used
- Python 3.11+
- FastAPI
- MongoDB Atlas
- Motor (async MongoDB driver)
- Pydantic
- Uvicorn

## Features
- Upload and retrieve sprite images
- Upload and retrieve audio files
- Submit and retrieve player scores
- Secure API with authentication
- MongoDB Atlas integration

## Setup Instructions
1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the environment: `source env/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your MongoDB connection string
6. Run the API: `uvicorn main:app --reload`

## API Endpoints
- `/sprites` - Manage game sprites
- `/audio` - Manage audio files
- `/scores` - Manage player scores

## Security Features
- API key authentication
- Input validation
- MongoDB Atlas security
- IP whitelisting