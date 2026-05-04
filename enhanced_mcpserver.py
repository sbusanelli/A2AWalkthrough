import json
import math
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Initialize the server
mcp = FastMCP("enhanced_doctorserver")

# Load Data
doctors: list = json.loads(Path("data/doctors.json").read_text())

# Mock availability data (in real implementation, this would come from a database)
availability_data = {
    "DOC001": {
        "next_available": "2026-05-06",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC002": {
        "next_available": "2026-05-05", 
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC011": {
        "next_available": "2026-05-04",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC012": {
        "next_available": "2026-05-04",
        "available_times": ["08:30", "10:30", "14:30", "16:30"]
    },
    "DOC013": {
        "next_available": "2026-05-15",
        "available_times": ["09:00", "11:00", "14:00"]
    },
    "DOC014": {
        "next_available": "2026-05-05",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC015": {
        "next_available": "2026-05-07",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC016": {
        "next_available": "2026-05-04",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC017": {
        "next_available": "2026-05-20",
        "available_times": ["10:00", "13:00"]
    },
    "DOC018": {
        "next_available": "2026-05-06",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC019": {
        "next_available": "2026-05-05",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC020": {
        "next_available": "2026-05-08",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC021": {
        "next_available": "2026-05-06",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC022": {
        "next_available": "2026-05-18",
        "available_times": ["09:00", "11:00", "14:00"]
    },
    "DOC023": {
        "next_available": "2026-05-05",
        "available_times": ["08:30", "10:30", "14:30", "16:30"]
    },
    "DOC024": {
        "next_available": "2026-05-10",
        "available_times": ["09:00", "11:00", "14:00"]
    },
    "DOC025": {
        "next_available": "2026-05-07",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC026": {
        "next_available": "2026-05-04",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC027": {
        "next_available": "2026-05-09",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC028": {
        "next_available": "2026-05-04",
        "available_times": ["24/7 Emergency"]
    },
    "DOC029": {
        "next_available": "2026-05-05",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC030": {
        "next_available": "2026-05-25",
        "available_times": ["09:00", "11:00"]
    },
    "DOC031": {
        "next_available": "2026-05-06",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC032": {
        "next_available": "2026-05-22",
        "available_times": ["10:00", "13:00"]
    },
    "DOC033": {
        "next_available": "2026-05-08",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC034": {
        "next_available": "2026-05-07",
        "available_times": ["08:30", "10:30", "14:30", "16:30"]
    },
    "DOC035": {
        "next_available": "2026-05-05",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC036": {
        "next_available": "2026-05-30",
        "available_times": ["10:00", "13:00"]
    },
    "DOC037": {
        "next_available": "2026-05-06",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC038": {
        "next_available": "2026-05-09",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC039": {
        "next_available": "2026-05-07",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC040": {
        "next_available": "2026-05-08",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC041": {
        "next_available": "2026-05-16",
        "available_times": ["09:00", "11:00", "14:00"]
    },
    "DOC042": {
        "next_available": "2026-05-05",
        "available_times": ["08:30", "10:30", "14:30", "16:30"]
    },
    "DOC043": {
        "next_available": "2026-05-12",
        "available_times": ["09:00", "11:00", "14:00"]
    },
    "DOC044": {
        "next_available": "2026-05-04",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC045": {
        "next_available": "2026-05-06",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    },
    "DOC046": {
        "next_available": "2026-05-09",
        "available_times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "DOC047": {
        "next_available": "2026-05-04",
        "available_times": ["24/7 Emergency"]
    },
    "DOC048": {
        "next_available": "2026-05-07",
        "available_times": ["10:00", "13:00", "15:00", "17:00"]
    },
    "DOC049": {
        "next_available": "2026-05-28",
        "available_times": ["09:00", "11:00"]
    },
    "DOC050": {
        "next_available": "2026-05-05",
        "available_times": ["08:00", "10:00", "13:00", "15:00"]
    }
}

# Mock insurance coverage data
insurance_networks = {
    "Blue Cross Blue Shield": ["DOC001", "DOC011", "DOC003", "DOC004", "DOC006", "DOC009", "DOC010", "DOC012", "DOC013", "DOC014", "DOC015", "DOC016", "DOC017", "DOC018", "DOC019", "DOC020", "DOC021", "DOC022", "DOC023", "DOC024", "DOC025", "DOC026", "DOC027", "DOC028", "DOC029", "DOC030", "DOC031", "DOC032", "DOC033", "DOC034", "DOC035", "DOC036", "DOC037", "DOC038", "DOC039", "DOC040", "DOC041", "DOC042", "DOC043", "DOC044", "DOC045", "DOC046", "DOC047", "DOC048", "DOC049", "DOC050"],
    "Aetna": ["DOC001", "DOC002", "DOC004", "DOC006", "DOC011", "DOC012", "DOC013", "DOC014", "DOC015", "DOC016", "DOC017", "DOC018", "DOC019", "DOC020", "DOC021", "DOC022", "DOC023", "DOC024", "DOC025", "DOC026", "DOC027", "DOC028", "DOC029", "DOC030", "DOC031", "DOC032", "DOC033", "DOC034", "DOC035", "DOC036", "DOC037", "DOC038", "DOC039", "DOC040", "DOC041", "DOC042", "DOC043", "DOC044", "DOC045", "DOC046", "DOC047", "DOC048", "DOC049", "DOC050"],
    "UnitedHealth": ["DOC001", "DOC002", "DOC003", "DOC010", "DOC011", "DOC012", "DOC014", "DOC015", "DOC016", "DOC017", "DOC018", "DOC020", "DOC021", "DOC022", "DOC023", "DOC024", "DOC025", "DOC026", "DOC027", "DOC028", "DOC029", "DOC030", "DOC031", "DOC032", "DOC033", "DOC034", "DOC035", "DOC036", "DOC037", "DOC038", "DOC039", "DOC040", "DOC041", "DOC042", "DOC043", "DOC044", "DOC045", "DOC046", "DOC047", "DOC048", "DOC049", "DOC050"],
    "Cigna": ["DOC001", "DOC003", "DOC004", "DOC010", "DOC013", "DOC014", "DOC015", "DOC017", "DOC020", "DOC021", "DOC022", "DOC024", "DOC025", "DOC027", "DOC032", "DOC033", "DOC034", "DOC036", "DOC039", "DOC040", "DOC043", "DOC044", "DOC046", "DOC048"],
    "Humana": ["DOC002", "DOC005", "DOC011", "DOC012", "DOC016", "DOC021", "DOC026", "DOC035", "DOC045"],
    "Medicare": ["DOC005", "DOC010", "DOC012", "DOC016", "DOC018", "DOC019", "DOC026", "DOC030", "DOC035", "DOC037", "DOC038", "DOC045", "DOC049", "DOC050"],
    "Medicaid": ["DOC002", "DOC005", "DOC007", "DOC012", "DOC016", "DOC019", "DOC023", "DOC026", "DOC035", "DOC038", "DOC042", "DOC045", "DOC050"]
}

@mcp.tool()
def list_doctors(state: str | None = None, city: str | None = None) -> list[dict]:
    """This tool returns a list of doctors practicing in a specific location. The search is case-insensitive.

    Args:
        state: The two-letter state code (e.g., "CA" for California).
        city: The name of the city or town (e.g., "Boston").

    Returns:
        A JSON string representing a list of doctors matching the criteria.
        If no criteria are provided, an error message is returned.
        Example: '[{"name": "Dr John James", "specialty": "Cardiology", ...}]'
    """
    # Input validation: ensure at least one search term is given.
    if not state and not city:
        return [{"error": "Please provide a state or a city."}]

    target_state = state.strip().lower() if state else None
    target_city = city.strip().lower() if city else None

    return [
        doc
        for doc in doctors
        if (not target_state or doc["address"]["state"].lower() == target_state)
        and (not target_city or doc["address"]["city"].lower() == target_city)
    ]

@mcp.tool()
def check_insurance_compatibility(provider_ids: list[str], insurance_plan: str) -> dict:
    """Check which providers accept a specific insurance plan.

    Args:
        provider_ids: List of provider IDs to check.
        insurance_plan: Name of the insurance plan.

    Returns:
        Dictionary with compatible and incompatible providers.
    """
    compatible_providers = []
    incompatible_providers = []
    
    network_providers = insurance_networks.get(insurance_plan, [])
    
    for provider_id in provider_ids:
        provider = next((doc for doc in doctors if doc["id"] == provider_id), None)
        if provider:
            if provider_id in network_providers or insurance_plan in provider.get("insurance_accepted", []):
                compatible_providers.append(provider)
            else:
                incompatible_providers.append(provider)
    
    return {
        "compatible": compatible_providers,
        "incompatible": incompatible_providers,
        "insurance_plan": insurance_plan
    }

@mcp.tool()
def calculate_distance(user_location: dict, provider_addresses: list[dict]) -> list[dict]:
    """Calculate distances from user location to multiple providers.

    Args:
        user_location: Dict with 'lat' and 'lon' coordinates.
        provider_addresses: List of provider address dictionaries.

    Returns:
        List of providers with calculated distances.
    """
    # Mock coordinates for cities (in real implementation, use geocoding API)
    city_coordinates = {
        "Austin, TX": {"lat": 30.2672, "lon": -97.7431},
        "Boston, MA": {"lat": 42.3601, "lon": -71.0589},
        "Atlanta, GA": {"lat": 33.7490, "lon": -84.3880},
        "Seattle, WA": {"lat": 47.6062, "lon": -122.3321},
        "Chicago, IL": {"lat": 41.8781, "lon": -87.6298},
        "Houston, TX": {"lat": 29.7604, "lon": -95.3698},
        "Denver, CO": {"lat": 39.7392, "lon": -104.9903},
        "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437},
        "Miami, FL": {"lat": 25.7617, "lon": -80.1918},
        "Nashville, TN": {"lat": 36.1627, "lon": -86.7816},
        "Phoenix, AZ": {"lat": 33.4484, "lon": -112.0740}
    }
    
    results = []
    user_lat = user_location.get("lat")
    user_lon = user_location.get("lon")
    
    for provider in provider_addresses:
        provider_city = f"{provider['address']['city']}, {provider['address']['state']}"
        provider_coords = city_coordinates.get(provider_city, {"lat": 0, "lon": 0})
        
        # Simple distance calculation (Haversine formula approximation)
        if user_lat and user_lon:
            distance = math.sqrt(
                (provider_coords["lat"] - user_lat)**2 + 
                (provider_coords["lon"] - user_lon)**2
            ) * 69  # Convert to miles (rough approximation)
        else:
            distance = 0
        
        provider_copy = provider.copy()
        provider_copy["distance_miles"] = round(distance, 1)
        results.append(provider_copy)
    
    return results

@mcp.tool()
def check_provider_availability(provider_ids: list[str], date_range: str | None = None) -> dict:
    """Check availability for multiple providers.

    Args:
        provider_ids: List of provider IDs to check.
        date_range: Optional date range for availability (e.g., "this_week", "next_week").

    Returns:
        Dictionary with provider availability information.
    """
    availability_info = {}
    
    for provider_id in provider_ids:
        provider = next((doc for doc in doctors if doc["id"] == provider_id), None)
        if provider:
            avail_data = availability_data.get(provider_id, {
                "next_available": "2026-05-10",
                "available_times": ["09:00", "14:00"]
            })
            
            availability_info[provider_id] = {
                "provider_name": provider["name"],
                "next_available": avail_data["next_available"],
                "available_times": avail_data["available_times"],
                "accepting_new_patients": provider.get("accepts_new_patients", False)
            }
    
    return availability_info

@mcp.tool()
def filter_by_specialty_keywords(query: str, providers: list[dict]) -> list[dict]:
    """Filter providers based on specialty keywords in natural language query.

    Args:
        query: Natural language query containing specialty keywords.
        providers: List of providers to filter.

    Returns:
        Filtered list of providers matching specialty keywords.
    """
    # Specialty keyword mapping
    specialty_keywords = {
        "heart": ["Cardiology"],
        "cardiac": ["Cardiology"], 
        "chest pain": ["Cardiology"],
        "mind": ["Psychiatry"],
        "mental health": ["Psychiatry"],
        "psychiatrist": ["Psychiatry"],
        "therapy": ["Psychiatry"],
        "counseling": ["Psychiatry"],
        "depression": ["Psychiatry"],
        "anxiety": ["Psychiatry"],
        "skin": ["Dermatology"],
        "rash": ["Dermatology"],
        "bones": ["Orthopedic Surgery"],
        "joint": ["Orthopedic Surgery"],
        "children": ["Pediatrics"],
        "kids": ["Pediatrics"],
        "baby": ["Pediatrics"],
        "stomach": ["Internal Medicine"],
        "digestive": ["Internal Medicine"],
        "brain": ["Neurology"],
        "headache": ["Neurology"],
        "migraine": ["Neurology"],
        "women": ["Obstetrics & Gynecology"],
        "pregnancy": ["Obstetrics & Gynecology"],
        "emergency": ["Emergency Medicine"],
        "cancer": ["Oncology"],
        "tumor": ["Oncology"]
    }
    
    query_lower = query.lower()
    matching_specialties = []
    
    for keyword, specialties in specialty_keywords.items():
        if keyword in query_lower:
            matching_specialties.extend(specialties)
    
    if not matching_specialties:
        return providers  # Return all if no keywords found
    
    # Remove duplicates
    matching_specialties = list(set(matching_specialties))
    
    filtered_providers = []
    for provider in providers:
        if provider["specialty"] in matching_specialties:
            filtered_providers.append(provider)
    
    return filtered_providers

@mcp.tool()
def rank_providers_by_criteria(providers: list[dict], criteria: dict) -> list[dict]:
    """Rank providers based on multiple criteria (distance, availability, insurance).

    Args:
        providers: List of providers to rank.
        criteria: Dict containing ranking preferences (weights and priorities).

    Returns:
        Ranked list of providers with scores.
    """
    ranked_providers = []
    
    for provider in providers:
        score = 0
        provider_copy = provider.copy()
        
        # Distance scoring (closer is better)
        distance = provider_copy.get("distance_miles", 100)
        if distance <= 5:
            score += 30
        elif distance <= 10:
            score += 20
        elif distance <= 25:
            score += 10
        
        # Availability scoring
        if provider_copy.get("accepts_new_patients", False):
            score += 25
        
        # Insurance compatibility (if specified)
        if criteria.get("insurance_plan"):
            insurance_accepted = provider_copy.get("insurance_accepted", [])
            if criteria["insurance_plan"] in insurance_accepted:
                score += 25
        
        # Experience scoring
        years_experience = provider_copy.get("years_experience", 0)
        if years_experience >= 15:
            score += 10
        elif years_experience >= 10:
            score += 7
        elif years_experience >= 5:
            score += 5
        
        # Board certification
        if provider_copy.get("board_certified", False):
            score += 10
        
        provider_copy["ranking_score"] = score
        ranked_providers.append(provider_copy)
    
    # Sort by score (descending)
    ranked_providers.sort(key=lambda x: x["ranking_score"], reverse=True)
    
    return ranked_providers

# Kick off server if file is run
if __name__ == "__main__":
    mcp.run(transport="stdio")
