from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime
import os
import httpx

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY
}

# Bundesliga = League ID 78, Season 2026
LEAGUE_ID = 78
SEASON = 2026

def get_api_football_team_id(openliga_id: int):
    """Mapped openliga IDs to API-Football IDs"""
    mapping = {
        40: 157,   # FC Bayern München
        7: 165,    # Borussia Dortmund
        6: 168,    # Bayer Leverkusen
        91: 169,   # Eintracht Frankfurt
        1635: 173, # RB Leipzig
        87: 163,   # Borussia Mönchengladbach
        16: 172,   # VfB Stuttgart
        134: 162,  # SV Werder Bremen
        175: 167,  # TSG Hoffenheim
        112: 160,  # SC Freiburg
        95: 170,   # FC Augsburg
        81: 164,   # FSV Mainz 05
        80: 182,   # Union Berlin
        65: 192,   # 1. FC Köln
        100: 180,  # Hamburger SV
        9: 174,    # FC Schalke 04
        31: 191,   # SC Paderborn
        198: 1003  # SV Elversberg
    }
    return mapping.get(openliga_id)

def seed_players_from_api():
    print("Spieler werden von API-Football abgerufen...")
    
    teams = supabase.table("teams").select("*").execute().data
    
    for team in teams:
        api_team_id = get_api_football_team_id(team["openliga_id"])
        
        if not api_team_id:
            print(f"⚠️ Kein API-Football Mapping für {team['name']}")
            continue
        
        response = httpx.get(
            f"https://v3.football.api-sports.io/players/squads",
            headers=HEADERS,
            params={"team": api_team_id}
        )
        
        if response.status_code != 200:
            print(f"⚠️ Fehler bei {team['name']}: {response.status_code}")
            continue
        
        data = response.json()
        players = data.get("response", [])
        
        if not players:
            print(f"⚠️ Keine Spieler für {team['name']}")
            continue
        
        player_list = players[0].get("players", [])
        count = 0
        
        for player in player_list:
            position_map = {
                "Goalkeeper": "TW",
                "Defender": "AB",
                "Midfielder": "MF",
                "Attacker": "ST"
            }
            position = position_map.get(player.get("position", ""), "Unbekannt")
            
            data_row = {
                "name": player["name"],
                "team_id": team["id"],
                "position": position
            }
            
            supabase.table("players").upsert(
                data_row, on_conflict="name,team_id"
            ).execute()
            count += 1
        
        print(f"✅ {count} Spieler für {team['name']} eingetragen")
    
    print("\nFertig! Alle Spieler sind in der Datenbank.")

if __name__ == "__main__":
    seed_players_from_api()