from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
import os
import httpx

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

@app.post("/lineups/fetch/{matchday_number}")
def fetch_real_lineups(matchday_number: int):
    # Spieltag von OpenLiga DB abrufen
    response = httpx.get(f"https://api.openligadb.de/getmatchdata/bl1/2026/{matchday_number}")
    
    if response.status_code != 200:
        return {"error": "Spieltag nicht gefunden"}
    
    matches = response.json()
    matchday = supabase.table("matchdays").select("*").eq("matchday_number", matchday_number).eq("season", "2026/27").execute()
    
    if not matchday.data:
        return {"error": "Spieltag nicht in Datenbank gefunden"}
    
    matchday_id = matchday.data[0]["id"]
    saved = 0
    
    for match in matches:
        for team_data in [{"id": match["team1"]["teamId"], "players": match.get("team1", {})}, 
                          {"id": match["team2"]["teamId"], "players": match.get("team2", {})}]:
            
            team = supabase.table("teams").select("*").eq("openliga_id", team_data["id"]).execute()
            if not team.data:
                continue
            
            team_id = team.data[0]["id"]
            lineup = match.get("matchResults", [])
            
            # Spieler aus der Aufstellung holen
            players = supabase.table("players").select("*").eq("team_id", team_id).execute()
            
            for player in players.data[:11]:  # Erste 11 als Startelf
                data = {
                    "matchday_id": matchday_id,
                    "team_id": team_id,
                    "player_id": player["id"]
                }
                supabase.table("real_lineups").upsert(
                    data, on_conflict="matchday_id,team_id,player_id"
                ).execute()
                saved += 1
    
    return {"message": f"{saved} Lineup-Einträge gespeichert"}

@app.post("/scores/calculate/{matchday_number}")
def calculate_scores(matchday_number: int):
    matchday = supabase.table("matchdays").select("*").eq("matchday_number", matchday_number).eq("season", "2026/27").execute()
    
    if not matchday.data:
        return {"error": "Spieltag nicht gefunden"}
    
    matchday_id = matchday.data[0]["id"]
    
    # Alle echten Aufstellungen für diesen Spieltag
    real_lineups = supabase.table("real_lineups").select("*").eq("matchday_id", matchday_id).execute()
    real_player_ids = {(r["team_id"], r["player_id"]) for r in real_lineups.data}
    
    # Alle Predictions für diesen Spieltag
    predictions = supabase.table("predictions").select("*").eq("matchday_id", matchday_id).execute()
    
    # Punkte pro User und Team berechnen
    scores = {}
    for pred in predictions.data:
        key = (pred["user_id"], pred["team_id"])
        if key not in scores:
            scores[key] = 0
        if (pred["team_id"], pred["player_id"]) in real_player_ids:
            scores[key] += 1
    
    # Scores speichern
    for (user_id, team_id), points in scores.items():
        data = {
            "user_id": user_id,
            "matchday_id": matchday_id,
            "team_id": team_id,
            "points": points
        }
        supabase.table("scores").upsert(
            data, on_conflict="user_id,matchday_id,team_id"
        ).execute()
    
    return {"message": f"Scores für {len(scores)} User-Team Kombinationen berechnet"}