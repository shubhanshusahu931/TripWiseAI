import json
import logging
import httpx
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompt enforcing strict structured JSON schema
SYSTEM_PROMPT = """You are TripWise AI, a world-class travel planner and itinerary specialist.
Your goal is to generate realistic, optimized, day-by-day personalized travel itineraries.
You MUST output ONLY a valid JSON object matching the exact structure specified below. Do not wrap in markdown quotes if possible, or use standard ```json.

Structure of the expected JSON:
{
  "summary": "High-level overview of the trip experience, highlighting key themes and vibes.",
  "days": [
    {
      "day_number": 1,
      "theme": "Arrival & City Landmarks",
      "activities": [
        {
          "title": "Visit Landmark Name",
          "description": "Engaging description of the attraction, what to see and do.",
          "time_slot": "Morning",
          "start_time": "09:30",
          "end_time": "11:30",
          "location": "District or specific address",
          "duration_minutes": 120,
          "estimated_cost": 25.0,
          "currency": "USD",
          "transportation_suggestion": "Take Metro Line 1 to Station X, 5 min walk.",
          "practical_tips": "Book tickets online in advance to skip the queue."
        }
      ]
    }
  ]
}

Ensure:
- Day-wise schedules are paced appropriately (relaxed: 2 activities/day; balanced: 3-4 activities/day; packed: 5 activities/day).
- Group nearby attractions together geographically to minimize transit time.
- Time slots should be 'Morning', 'Afternoon', 'Evening', or 'Night'.
- Estimated costs should realistically reflect the user's travel style (budget, standard, luxury).
- Include practical advice (dress codes, booking tips, best vantage points).
"""

async def generate_itinerary_with_llm(trip: Dict[str, Any], prompt_notes: Optional[str] = None) -> Dict[str, Any]:
    dest = trip.get("destination", "Paris")
    start = trip.get("start_date", "2026-06-01")
    end = trip.get("end_date", "2026-06-03")
    travelers = trip.get("num_travelers", 1)
    budget = trip.get("total_budget", 1000)
    currency = trip.get("currency", "USD")
    style = trip.get("travel_style", "standard")
    pace = trip.get("travel_pace", "balanced")
    interests = trip.get("interests", [])
    dietary = trip.get("dietary_restrictions", [])
    accommodation = trip.get("accommodation_preference", "hotel")
    notes = trip.get("additional_notes", "")

    # Calculate days count
    try:
        d1 = datetime.strptime(str(start), "%Y-%m-%d").date()
        d2 = datetime.strptime(str(end), "%Y-%m-%d").date()
        num_days = max(1, (d2 - d1).days + 1)
    except Exception:
        num_days = 3

    user_prompt = f"""Plan a {num_days}-day trip to {dest} for {travelers} traveler(s).
Start Date: {start}
End Date: {end}
Budget: {budget} {currency}
Travel Style: {style}
Travel Pace: {pace}
Interests: {', '.join(interests) if interests else 'General sightseeing, local food, culture'}
Accommodation: {accommodation}
Dietary Restrictions: {', '.join(dietary) if dietary else 'None'}
Additional Preferences: {notes}
{f'Custom User Refinement: {prompt_notes}' if prompt_notes else ''}

Generate exactly {num_days} days. Return ONLY valid JSON."""

    # 1. Attempt Live LLM call if configured
    if settings.AI_API_KEY and settings.AI_PROVIDER != "mock":
        try:
            if settings.AI_PROVIDER == "gemini":
                result = await _call_gemini(user_prompt)
                if result:
                    result["is_sample_data"] = False
                    return result
            elif settings.AI_PROVIDER in ("openai", "groq", "openrouter"):
                result = await _call_openai_compatible(user_prompt)
                if result:
                    result["is_sample_data"] = False
                    return result
        except Exception as e:
            logger.error(f"Error calling LLM provider {settings.AI_PROVIDER}: {e}")

    # 2. Smart Curated Fallback Engine (labeled as sample data)
    return _generate_smart_fallback(trip, num_days)

async def _call_gemini(prompt: str) -> Optional[Dict[str, Any]]:
    model = settings.AI_MODEL or "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.AI_API_KEY}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\n\nUser Request:\n{prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.7
        }
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(url, json=payload)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)
    return None

async def _call_openai_compatible(prompt: str) -> Optional[Dict[str, Any]]:
    base_url = settings.AI_BASE_URL or "https://api.openai.com/v1"
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json"
    }
    model = settings.AI_MODEL or "gpt-4o-mini"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["choices"][0]["message"]["content"]
            return json.loads(raw_text)
    return None

# --- Curated Landmark Knowledge Base for Smart Fallback ---
DESTINATION_TEMPLATES = {
    "tokyo": [
        ("Sensō-ji Temple & Asakusa Old Town", "Morning", "09:00", "11:30", "Explore Tokyo's oldest temple, stroll Nakamise shopping street, and try freshly made melonpan.", 15.0, "Subway: Ginza Line to Asakusa Station", "Visit early morning before crowds peak."),
        ("Tokyo Skytree Observation Deck", "Afternoon", "12:30", "14:30", "Enjoy 360-degree panoramic skyline views across the Kanto plain up to Mt. Fuji on clear days.", 27.0, "Walk 15 mins from Asakusa or take Tobu Skytree Line", "Book fast-track ticket online to skip the main queue."),
        ("Shibuya Crossing & Hachiko Plaza", "Evening", "16:00", "18:30", "Experience the world's busiest pedestrian scramble, snap photos with Hachiko statue, and explore Shibuya 109.", 0.0, "Hanzomon Subway Line directly to Shibuya", "Great viewing spots from the 2nd floor Starbucks overlooking the crossing."),
        ("Meiji Jingu Shrine & Yoyogi Park", "Morning", "09:00", "11:00", "Serene Shinto shrine enveloped in an evergreen forest of over 100,000 sacred trees.", 5.0, "JR Yamanote Line to Harajuku Station", "Write a wooden ema prayer tablet for good luck."),
        ("Harajuku Takeshita Street & Omotesando", "Afternoon", "11:30", "14:00", "Vibrant youth pop culture, quirky boutiques, Japanese crepes, and architectural avenue.", 20.0, "Walk 2 minutes from Harajuku Station", "Try street food and matcha soft-serve."),
        ("Shinjuku Omoide Yokocho & Golden Gai", "Night", "18:30", "21:30", "Atmospheric narrow alleyways packed with historic yakitori stalls and intimate micro-bars.", 45.0, "JR Yamanote Line to Shinjuku East Exit", "Bring cash as many traditional stalls don't accept foreign cards.")
    ],
    "paris": [
        ("Eiffel Tower & Champ de Mars", "Morning", "09:30", "12:00", "Ascend the iconic Iron Lady for sweeping vistas of the Seine and Parisian boulevards.", 32.0, "Metro Line 6 to Bir-Hakeim or RER C to Champ de Mars", "Arrive 15 mins prior to your elevator reservation slot."),
        ("Louvre Museum & Cour Napoléon", "Afternoon", "13:30", "16:30", "World's largest museum featuring Mona Lisa, Venus de Milo, and the Winged Victory.", 22.0, "Metro Line 1 or 7 to Palais-Royal Musée du Louvre", "Enter via Carrousel du Louvre underground mall for shorter security lines."),
        ("Seine River Evening Cruise", "Evening", "18:00", "19:30", "Glamp along the river witnessing illuminated bridges and Gothic architecture at golden hour.", 18.0, "Departs near Pont Neuf or Pont de l'Alma", "Sit on the open upper deck for uninterrupted photo views."),
        ("Montmartre & Sacré-Cœur Basilica", "Morning", "09:30", "12:00", "Historic hilltop artists' quarter, cobblestone alleys, Place du Tertre, and basilica dome.", 8.0, "Metro Line 2 to Anvers + Montmartre Funicular", "Beware of street bracelet vendors around the main staircase."),
        ("Musée d'Orsay & Left Bank Stroll", "Afternoon", "13:30", "16:00", "Masterpieces of Impressionism housed in a grand former Beaux-Arts railway station.", 16.0, "RER C to Musée d'Orsay", "Grab coffee near the giant vintage station clock face.")
    ],
    "new york": [
        ("Central Park & Bethesda Terrace", "Morning", "09:00", "11:30", "Peaceful stroll through Manhattan's 843-acre urban sanctuary, Bow Bridge, and the Mall.", 0.0, "Subway N, Q, R, W to 5th Ave/59th St", "Rent a Citi Bike for quicker cross-park transit."),
        ("Metropolitan Museum of Art (The Met)", "Afternoon", "12:30", "15:30", "Five thousand years of world art, from the Temple of Dendur to American wing treasures.", 30.0, "Walk across 5th Avenue from Central Park", "Head up to the Cantor Rooftop Garden for skyline views in summer."),
        ("Times Square & Broadway Theater District", "Evening", "17:30", "21:30", "Electrifying neon spectacle, flagship megastores, and an unforgettable Broadway show.", 85.0, "Subway 1, 2, 3, 7, N, Q, R, W to 42nd St", "Check the TKTS booth under the red steps for same-day discount tickets.")
    ]
}

def _generate_smart_fallback(trip: Dict[str, Any], num_days: int) -> Dict[str, Any]:
    dest = trip.get("destination", "Paris")
    dest_lower = dest.lower()
    currency = trip.get("currency", "USD")
    style = trip.get("travel_style", "standard")
    multiplier = 0.6 if style == "budget" else (2.0 if style == "luxury" else 1.0)

    # Pick matching landmarks or build dynamic destination items
    matched_key = None
    for k in DESTINATION_TEMPLATES:
        if k in dest_lower:
            matched_key = k
            break

    template_items = DESTINATION_TEMPLATES.get(matched_key) if matched_key else None

    days_data = []
    for day_idx in range(1, num_days + 1):
        day_theme = f"Exploring {dest} - Chapter {day_idx}"
        activities = []

        if template_items:
            # Cycle through template items
            offset = (day_idx - 1) * 3
            day_acts = [template_items[(offset + i) % len(template_items)] for i in range(3)]
            for title, slot, st, et, desc, cost, trans, tips in day_acts:
                activities.append({
                    "title": title,
                    "description": desc,
                    "time_slot": slot,
                    "start_time": st,
                    "end_time": et,
                    "location": f"{dest} City Center",
                    "duration_minutes": 120,
                    "estimated_cost": round(cost * multiplier, 2),
                    "currency": currency,
                    "transportation_suggestion": trans,
                    "practical_tips": tips
                })
        else:
            # Dynamic generic landmarks for any world destination
            activities = [
                {
                    "title": f"Historic Old Town & Cultural Discovery in {dest}",
                    "description": f"Start your journey delving into the rich history, architecture, and iconic squares of {dest}.",
                    "time_slot": "Morning",
                    "start_time": "09:30",
                    "end_time": "12:00",
                    "location": f"Historic Center, {dest}",
                    "duration_minutes": 150,
                    "estimated_cost": round(15.0 * multiplier, 2),
                    "currency": currency,
                    "transportation_suggestion": "Central public transit or pleasant walking route.",
                    "practical_tips": "Wear comfortable walking shoes for cobblestone streets."
                },
                {
                    "title": f"{dest} City Museum & Landmark Tour",
                    "description": f"Experience signature exhibits, local art, and panoramic viewpoints overlooking {dest}.",
                    "time_slot": "Afternoon",
                    "start_time": "13:30",
                    "end_time": "16:00",
                    "location": f"Cultural District, {dest}",
                    "duration_minutes": 150,
                    "estimated_cost": round(25.0 * multiplier, 2),
                    "currency": currency,
                    "transportation_suggestion": "Metro / local bus or short taxi ride.",
                    "practical_tips": "Audio guides are recommended to discover hidden folklore."
                },
                {
                    "title": f"Local Gastronomy & Sunset Promenade in {dest}",
                    "description": f"Dine at authentic local eateries, sample signature delicacies, and enjoy evening city lights.",
                    "time_slot": "Evening",
                    "start_time": "18:00",
                    "end_time": "20:30",
                    "location": f"Waterfront / Dining Quarter, {dest}",
                    "duration_minutes": 150,
                    "estimated_cost": round(40.0 * multiplier, 2),
                    "currency": currency,
                    "transportation_suggestion": "Walk along the main pedestrian boulevard.",
                    "practical_tips": "Make a dinner reservation if traveling on a weekend."
                }
            ]

        days_data.append({
            "day_number": day_idx,
            "theme": day_theme,
            "activities": activities
        })

    return {
        "summary": f"Curated {num_days}-day itinerary for {dest} tailored to {style} travel pace. [Sample Data / Fallback Engine: Configure AI_API_KEY in .env for live LLM generation]",
        "is_sample_data": True,
        "days": days_data
    }

async def regenerate_single_day(trip: Dict[str, Any], day_number: int, prompt_notes: Optional[str] = None) -> List[Dict[str, Any]]:
    """Regenerates 3 activities for a specific day"""
    dest = trip.get("destination", "Paris")
    currency = trip.get("currency", "USD")
    style = trip.get("travel_style", "standard")
    multiplier = 0.6 if style == "budget" else (2.0 if style == "luxury" else 1.0)

    prompt = f"Regenerate day {day_number} of a trip to {dest}. Refinement notes: {prompt_notes or 'Provide unique alternative activities'}. Return 3 activities in JSON."
    
    if settings.AI_API_KEY and settings.AI_PROVIDER != "mock":
        try:
            if settings.AI_PROVIDER == "gemini":
                res = await _call_gemini(prompt)
                if res and "days" in res and res["days"]:
                    return res["days"][0].get("activities", [])
            elif settings.AI_PROVIDER in ("openai", "groq", "openrouter"):
                res = await _call_openai_compatible(prompt)
                if res and "days" in res and res["days"]:
                    return res["days"][0].get("activities", [])
        except Exception as e:
            logger.error(f"Error in regenerate_single_day LLM: {e}")

    # Fallback regenerated activities
    theme_note = f" (Focus: {prompt_notes})" if prompt_notes else ""
    return [
        {
            "day_number": day_number,
            "title": f"Artisanal Morning Discovery in {dest}{theme_note}",
            "description": f"Freshly regenerated morning experience exploring local bakeries, craft markets, and hidden alleys.",
            "time_slot": "Morning",
            "start_time": "09:00",
            "end_time": "11:30",
            "location": f"Artisanal District, {dest}",
            "duration_minutes": 150,
            "estimated_cost": round(18.0 * multiplier, 2),
            "currency": currency,
            "transportation_suggestion": "Short walk or local tram.",
            "practical_tips": "Great photography opportunities during morning light.",
            "is_custom": False
        },
        {
            "day_number": day_number,
            "title": f"Afternoon Hidden Gem & Scenic Park{theme_note}",
            "description": f"Escape the tourist crowd at a peaceful botanical garden or hilltop terrace with picturesque views.",
            "time_slot": "Afternoon",
            "start_time": "13:00",
            "end_time": "15:30",
            "location": f"Gardens of {dest}",
            "duration_minutes": 150,
            "estimated_cost": round(12.0 * multiplier, 2),
            "currency": currency,
            "transportation_suggestion": "Direct metro ride.",
            "practical_tips": "Bring a reusable water bottle and binoculars.",
            "is_custom": False
        },
        {
            "day_number": day_number,
            "title": f"Authentic Twilight Food Tour & Night Market{theme_note}",
            "description": f"Taste delicacies hand-picked by local foodies, with evening music and vibrant atmosphere.",
            "time_slot": "Evening",
            "start_time": "18:00",
            "end_time": "21:00",
            "location": f"Night District, {dest}",
            "duration_minutes": 180,
            "estimated_cost": round(45.0 * multiplier, 2),
            "currency": currency,
            "transportation_suggestion": "Local transit or short cab ride.",
            "practical_tips": "Cash preferred at market stalls.",
            "is_custom": False
        }
    ]
