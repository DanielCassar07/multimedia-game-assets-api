from fastapi import FastAPI
import sys
import os

# added the parent directory to path so I can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app from main.py
from main import app

