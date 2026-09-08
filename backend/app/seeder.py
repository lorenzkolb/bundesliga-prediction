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