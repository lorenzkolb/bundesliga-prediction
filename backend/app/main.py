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

@app.post("/predictions")
def create_prediction(prediction: dict):
    # Prüfen ob Deadline bereits abgelaufen ist
    matchday = supabase.table("matchdays").select("*").eq("id", prediction["matchday_id"]).execute()
    
    if not matchday.data:
        return {"error": "Spieltag nicht gefunden"}
    
    deadline = matchday.data[0]["deadline"]
    
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    
    if now > deadline:
        return {"error": "Deadline abgelaufen - keine Predictions mehr möglich"}
    
    # Prediction speichern
    data = {
        "user_id": prediction["user_id"],
        "matchday_id": prediction["matchday_id"],
        "team_id": prediction["team_id"],
        "player_id": prediction["player_id"]
    }
    
    response = supabase.table("predictions").insert(data).execute()
    return response.data