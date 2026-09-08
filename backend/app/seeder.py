from supabase import create_client
from dotenv import load_dotenv
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

if __name__ == "__main__":
    seed_teams()


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

if __name__ == "__main__":
    seed_teams()
    seed_players()