from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import random
import requests

app = FastAPI(title="Rainwater Harvesting Backend")

# ✅ Enable CORS so Lovable frontend works
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check
@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend running successfully on Render!"}


# ✅ Rooftop segmentation (mock AI with multiple file support)
@app.post("/api/segment")
async def segment_rooftop(files: List[UploadFile] = File(...)):
    """
    Accepts multiple images or video files.
    Returns a simulated rooftop area for each.
    """
    results = []
    for f in files:
        fake_area = round(random.uniform(40.0, 250.0), 2)  # sqm
        results.append({
            "filename": f.filename,
            "detected_area_sqm": fake_area,
            "message": "AI detected rooftop successfully (mock)"
        })
    return {"rooftops": results}


# ✅ Rainwater harvesting calculator with overflow
@app.post("/api/calc")
async def calculate_harvesting(
    area: float = Form(...),        # sqm
    rainfall: float = Form(...),    # mm/year
    efficiency: float = Form(0.8),  # default 80%
    tank_capacity: float = Form(10000.0)  # liters
):
    """
    Calculates harvested water based on rooftop area & rainfall.
    Also checks if tank overflows.
    """
    potential = area * rainfall * efficiency  # liters/year

    overflow = max(0, potential - tank_capacity)
    stored = min(potential, tank_capacity)

    return {
        "area_sqm": area,
        "rainfall_mm": rainfall,
        "efficiency": efficiency,
        "harvested_liters": round(potential, 2),
        "tank_capacity_liters": tank_capacity,
        "stored_liters": round(stored, 2),
        "overflow_liters": round(overflow, 2),
        "message": "Overflow detected!" if overflow > 0 else "Safe storage"
    }


# ✅ Rainfall prediction API (Open-Meteo)
@app.get("/api/rainfall")
def get_rainfall(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto"
    try:
        response = requests.get(url, timeout=10).json()
        rainfall_data = response.get("daily", {}).get("precipitation_sum", [])
        return {
            "location": {"lat": lat, "lon": lon},
            "rainfall_prediction_mm": rainfall_data
        }
    except Exception as e:
        return {"error": str(e)}


# ✅ Soil data API (SoilGrids)
@app.get("/api/soil")
def get_soil(lat: float, lon: float):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=clay&depth=15-30cm"
    try:
        response = requests.get(url, timeout=10).json()
        clay_content = response.get("properties", {}).get("clay", {})
        return {
            "location": {"lat": lat, "lon": lon},
            "clay_content": clay_content,
            "interpretation": "Medium infiltration → recharge pit recommended"
        }
    except Exception as e:
        return {"error": str(e)}


# ✅ Voice/chat assistant
@app.post("/api/voice/text")
async def voice_agent(query: str = Form(...)):
    responses = {
        "rainwater": "Rainwater harvesting stores rainwater and recharges groundwater.",
        "soil": "Soil in your area has medium infiltration capacity, so a recharge pit is recommended.",
        "overflow": "If your tank overflows, you should divert extra water to recharge pits or nearby green spaces.",
        "default": "Hello! I am your Rainwater Voice Assistant. Ask me about rainwater, soil, or overflow."
    }
    if "rain" in query.lower():
        return {"response": responses["rainwater"]}
    elif "soil" in query.lower():
        return {"response": responses["soil"]}
    elif "overflow" in query.lower():
        return {"response": responses["overflow"]}
    else:
        return {"response": responses["default"]}


# ✅ GIS/Map integration (basic mock endpoint for frontend maps)
@app.get("/api/adoptions")
def adoption_map():
    """
    Returns mock data of users adopting rooftop harvesting,
    to be plotted on frontend map (GIS).
    """
    return {
        "adoptions": [
            {"lat": 19.0760, "lon": 72.8777, "user": "Mumbai Home"},
            {"lat": 28.6139, "lon": 77.2090, "user": "Delhi School"},
            {"lat": 13.0827, "lon": 80.2707, "user": "Chennai NGO"},
        ]
    }
