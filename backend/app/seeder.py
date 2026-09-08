from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os
import httpx

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def seed_teams():
    print("Teams werden von OpenLiga DB abgerufen...")
    response = httpx.get("https://api.openligadb.de/getavailableteams/bl1/2026")
    teams = response.json()
    for team in teams:
        data = {
            "name": team["teamName"],
            "short_name": team["shortName"],
            "openliga_id": team["teamId"]
        }
        supabase.table("teams").upsert(data, on_conflict="openliga_id").execute()
        print(f"✅ {team['teamName']} eingetragen")
    print("Fertig! Alle Teams sind in der Datenbank.")

def seed_players():
    print("Spieler werden von OpenLiga DB abgerufen...")
    teams = supabase.table("teams").select("*").execute().data
    for team in teams:
        response = httpx.get(f"https://api.openligadb.de/getteamdata/{team['openliga_id']}")
        if response.status_code != 200:
            print(f"⚠️ Keine Daten für {team['name']}")
            continue
        team_data = response.json()
        players = team_data.get("players", [])
        for player in players:
            data = {
                "name": player["name"],
                "team_id": team["id"],
                "position": player.get("position", "Unbekannt")
            }
            supabase.table("players").upsert(data, on_conflict="name,team_id").execute()
        print(f"✅ {len(players)} Spieler für {team['name']} eingetragen")

def seed_matchdays():
    print("Spieltage werden von OpenLiga DB abgerufen...")
    for spieltag in range(1, 35):
        response = httpx.get(f"https://api.openligadb.de/getmatchdata/bl1/2026/{spieltag}")
        if response.status_code != 200:
            print(f"⚠️ Keine Daten für Spieltag {spieltag}")
            continue
        matches = response.json()
        if not matches:
            print(f"⚠️ Spieltag {spieltag} noch nicht verfügbar")
            continue
        
        # Erstes Spiel nehmen und 30 Minuten abziehen
        first_match_str = matches[0]["matchDateTimeUTC"]
        first_match = datetime.fromisoformat(first_match_str.replace("Z", "+00:00"))
        deadline = (first_match - timedelta(minutes=30)).isoformat()
        
        data = {
            "season": "2026/27",
            "matchday_number": spieltag,
            "deadline": deadline
        }
        supabase.table("matchdays").upsert(
            data, on_conflict="season,matchday_number"
        ).execute()
        print(f"✅ Spieltag {spieltag} eingetragen - Deadline: {deadline}")
    print("Fertig! Alle Spieltage sind in der Datenbank.")

if __name__ == "__main__":
    seed_matchdays()