from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

app = FastAPI(title="Bundesliga Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Bundesliga Prediction API läuft!"}

@app.get("/teams")
def get_teams():
    response = supabase.table("teams").select("*").execute()
    return response.data

@app.get("/teams/{team_id}/players")
def get_players(team_id: str):
    response = supabase.table("players").select("*").eq("team_id", team_id).execute()
    return response.data