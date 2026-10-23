import sqlite3
import json
import uuid
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from app.core.config import settings

def _get_connection():
    db_path = settings.LOCAL_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        display_name TEXT DEFAULT 'Travel Explorer',
        preferred_currency TEXT DEFAULT 'USD',
        preferred_travel_style TEXT DEFAULT 'standard',
        home_city TEXT,
        avatar_url TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        destination TEXT NOT NULL,
        origin TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        num_travelers INTEGER DEFAULT 1,
        total_budget REAL DEFAULT 0.0,
        currency TEXT DEFAULT 'USD',
        travel_style TEXT DEFAULT 'standard',
        interests TEXT DEFAULT '[]',
        travel_pace TEXT DEFAULT 'balanced',
        accommodation_preference TEXT DEFAULT 'hotel',
        dietary_restrictions TEXT DEFAULT '[]',
        transportation_preference TEXT DEFAULT 'public_transit',
        additional_notes TEXT,
        status TEXT DEFAULT 'planning',
        cover_image_url TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itineraries (
        id TEXT PRIMARY KEY,
        trip_id TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        summary TEXT,
        raw_ai_response TEXT,
        estimated_total_cost REAL DEFAULT 0.0,
        cost_breakdown TEXT,
        is_sample_data INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id TEXT PRIMARY KEY,
        itinerary_id TEXT NOT NULL,
        trip_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        day_number INTEGER NOT NULL,
        date TEXT,
        title TEXT NOT NULL,
        description TEXT,
        time_slot TEXT DEFAULT 'Morning',
        start_time TEXT DEFAULT '09:00',
        end_time TEXT DEFAULT '11:00',
        location TEXT,
        duration_minutes INTEGER DEFAULT 90,
        estimated_cost REAL DEFAULT 0.0,
        currency TEXT DEFAULT 'USD',
        transportation_suggestion TEXT,
        practical_tips TEXT,
        is_custom INTEGER DEFAULT 0,
        order_index INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    conn.commit()
    conn.close()

# Initialize tables on import
init_db()

# --- Destination Cover Image Helper ---
CURATED_IMAGES = {
    "tokyo": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
    "japan": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
    "paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80",
    "france": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80",
    "new york": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=1200&q=80",
    "nyc": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=1200&q=80",
    "rome": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=1200&q=80",
    "italy": "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=1200&q=80",
    "london": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=1200&q=80",
    "bali": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80",
    "indonesia": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1200&q=80",
    "dubai": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80",
    "barcelona": "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?auto=format&fit=crop&w=1200&q=80",
    "spain": "https://images.unsplash.com/photo-1543783207-ec64e4d95325?auto=format&fit=crop&w=1200&q=80",
    "sydney": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=1200&q=80",
    "bangkok": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=1200&q=80",
    "singapore": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=1200&q=80",
    "kyoto": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
    "amsterdam": "https://images.unsplash.com/photo-1512470876302-972faa2aa9a4?auto=format&fit=crop&w=1200&q=80",
    "default": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80"
}

def get_destination_image(destination: str) -> str:
    if not destination:
        return CURATED_IMAGES["default"]
    lower = destination.lower()
    for key, url in CURATED_IMAGES.items():
        if key in lower:
            return url
    return CURATED_IMAGES["default"]

# --- Profiles ---
def get_profile(user_id: str, email: str = "") -> Dict[str, Any]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    now = datetime.utcnow().isoformat()
    if not row:
        display_name = email.split("@")[0] if email else "Travel Explorer"
        cursor.execute(
            """INSERT INTO profiles (id, display_name, preferred_currency, preferred_travel_style, created_at, updated_at)
               VALUES (?, ?, 'USD', 'standard', ?, ?)""",
            (user_id, display_name, now, now)
        )
        conn.commit()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (user_id,))
        row = cursor.fetchone()
    conn.close()
    d = dict(row)
    d["email"] = email
    return d

def update_profile(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    conn = _get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    updates = []
    values = []
    for k in ["display_name", "preferred_currency", "preferred_travel_style", "home_city", "avatar_url"]:
        if k in data and data[k] is not None:
            updates.append(f"{k} = ?")
            values.append(data[k])
    if updates:
        updates.append("updated_at = ?")
        values.append(now)
        values.append(user_id)
        cursor.execute(f"UPDATE profiles SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    conn.close()
    return get_profile(user_id)

# --- Trips ---
def create_trip(user_id: str, trip_dict: Dict[str, Any]) -> Dict[str, Any]:
    conn = _get_connection()
    cursor = conn.cursor()
    trip_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    dest = trip_dict.get("destination", "")
    title = trip_dict.get("title") or f"Trip to {dest}"
    cover = trip_dict.get("cover_image_url") or get_destination_image(dest)

    cursor.execute(
        """INSERT INTO trips (
            id, user_id, title, destination, origin, start_date, end_date,
            num_travelers, total_budget, currency, travel_style, interests,
            travel_pace, accommodation_preference, dietary_restrictions,
            transportation_preference, additional_notes, status, cover_image_url,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            trip_id,
            user_id,
            title,
            dest,
            trip_dict.get("origin", ""),
            str(trip_dict.get("start_date")),
            str(trip_dict.get("end_date")),
            int(trip_dict.get("num_travelers", 1)),
            float(trip_dict.get("total_budget", 0.0)),
            trip_dict.get("currency", "USD"),
            trip_dict.get("travel_style", "standard"),
            json.dumps(trip_dict.get("interests", [])),
            trip_dict.get("travel_pace", "balanced"),
            trip_dict.get("accommodation_preference", "hotel"),
            json.dumps(trip_dict.get("dietary_restrictions", [])),
            trip_dict.get("transportation_preference", "public_transit"),
            trip_dict.get("additional_notes", ""),
            trip_dict.get("status", "planning"),
            cover,
            now,
            now
        )
    )
    conn.commit()
    conn.close()
    return get_trip(trip_id, user_id)

def get_trip(trip_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["interests"] = json.loads(d["interests"]) if d["interests"] else []
    d["dietary_restrictions"] = json.loads(d["dietary_restrictions"]) if d["dietary_restrictions"] else []
    return d

def list_trips(user_id: str, search: Optional[str] = None, status: Optional[str] = None, sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM trips WHERE user_id = ?"
    params = [user_id]

    if search:
        query += " AND (destination LIKE ? OR title LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if status and status != "all":
        query += " AND status = ?"
        params.append(status)

    if sort_by == "budget_high":
        query += " ORDER BY total_budget DESC"
    elif sort_by == "budget_low":
        query += " ORDER BY total_budget ASC"
    elif sort_by == "date_soonest":
        query += " ORDER BY start_date ASC"
    else:
        query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    trips = []
    for r in rows:
        d = dict(r)
        d["interests"] = json.loads(d["interests"]) if d["interests"] else []
        d["dietary_restrictions"] = json.loads(d["dietary_restrictions"]) if d["dietary_restrictions"] else []
        trips.append(d)
    return trips

def update_trip(trip_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in updates.items():
        if v is not None:
            if k in ("interests", "dietary_restrictions"):
                fields.append(f"{k} = ?")
                values.append(json.dumps(v))
            else:
                fields.append(f"{k} = ?")
                values.append(str(v) if isinstance(v, (date, datetime)) else v)
    if not fields:
        conn.close()
        return get_trip(trip_id, user_id)

    now = datetime.utcnow().isoformat()
    fields.append("updated_at = ?")
    values.append(now)
    values.extend([trip_id, user_id])

    cursor.execute(f"UPDATE trips SET {', '.join(fields)} WHERE id = ? AND user_id = ?", values)
    conn.commit()
    conn.close()
    return get_trip(trip_id, user_id)

def delete_trip(trip_id: str, user_id: str) -> bool:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activities WHERE trip_id = ? AND user_id = ?", (trip_id, user_id))
    cursor.execute("DELETE FROM itineraries WHERE trip_id = ? AND user_id = ?", (trip_id, user_id))
    cursor.execute("DELETE FROM trips WHERE id = ? AND user_id = ?", (trip_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def duplicate_trip(trip_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    trip = get_trip(trip_id, user_id)
    if not trip:
        return None
    new_data = dict(trip)
    new_data.pop("id", None)
    new_data.pop("created_at", None)
    new_data.pop("updated_at", None)
    new_data["title"] = f"Copy of {trip['title']}"
    new_trip = create_trip(user_id, new_data)

    # Duplicate itinerary if present
    itinerary = get_itinerary(trip_id, user_id)
    if itinerary:
        new_itin = save_itinerary(
            trip_id=new_trip["id"],
            user_id=user_id,
            summary=itinerary.get("summary", ""),
            raw_ai_response=itinerary.get("raw_ai_response", {}),
            cost_breakdown=itinerary.get("cost_breakdown", {}),
            is_sample_data=itinerary.get("is_sample_data", False)
        )
        # Duplicate activities
        acts = get_activities(itinerary["id"])
        for act in acts:
            act_copy = dict(act)
            create_activity(
                itinerary_id=new_itin["id"],
                trip_id=new_trip["id"],
                user_id=user_id,
                act_dict=act_copy
            )
    return new_trip

# --- Itineraries & Activities ---
def get_itinerary(trip_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM itineraries WHERE trip_id = ? AND user_id = ?", (trip_id, user_id))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["raw_ai_response"] = json.loads(d["raw_ai_response"]) if d["raw_ai_response"] else {}
    d["cost_breakdown"] = json.loads(d["cost_breakdown"]) if d["cost_breakdown"] else {}
    d["is_sample_data"] = bool(d["is_sample_data"])
    return d

def save_itinerary(
    trip_id: str,
    user_id: str,
    summary: str,
    raw_ai_response: Dict[str, Any],
    cost_breakdown: Dict[str, Any],
    is_sample_data: bool = False
) -> Dict[str, Any]:
    conn = _get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("SELECT id FROM itineraries WHERE trip_id = ?", (trip_id,))
    existing = cursor.fetchone()

    total_cost = cost_breakdown.get("total", 0.0)
    if not total_cost:
        total_cost = sum(cost_breakdown.values()) if isinstance(cost_breakdown, dict) else 0.0

    if existing:
        itin_id = existing["id"]
        cursor.execute(
            """UPDATE itineraries SET
               summary = ?, raw_ai_response = ?, estimated_total_cost = ?,
               cost_breakdown = ?, is_sample_data = ?, updated_at = ?
               WHERE id = ?""",
            (
                summary,
                json.dumps(raw_ai_response),
                total_cost,
                json.dumps(cost_breakdown),
                1 if is_sample_data else 0,
                now,
                itin_id
            )
        )
    else:
        itin_id = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO itineraries (
                id, trip_id, user_id, summary, raw_ai_response,
                estimated_total_cost, cost_breakdown, is_sample_data,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                itin_id,
                trip_id,
                user_id,
                summary,
                json.dumps(raw_ai_response),
                total_cost,
                json.dumps(cost_breakdown),
                1 if is_sample_data else 0,
                now,
                now
            )
        )
    conn.commit()
    conn.close()
    return get_itinerary(trip_id, user_id)

def get_activities(itinerary_id: str) -> List[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM activities WHERE itinerary_id = ? ORDER BY day_number ASC, order_index ASC, start_time ASC",
        (itinerary_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_activity(itinerary_id: str, trip_id: str, user_id: str, act_dict: Dict[str, Any]) -> Dict[str, Any]:
    conn = _get_connection()
    cursor = conn.cursor()
    act_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cursor.execute(
        """INSERT INTO activities (
            id, itinerary_id, trip_id, user_id, day_number, date,
            title, description, time_slot, start_time, end_time,
            location, duration_minutes, estimated_cost, currency,
            transportation_suggestion, practical_tips, is_custom,
            order_index, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            act_id,
            itinerary_id,
            trip_id,
            user_id,
            int(act_dict.get("day_number", 1)),
            str(act_dict.get("date")) if act_dict.get("date") else None,
            act_dict.get("title", "New Activity"),
            act_dict.get("description", ""),
            act_dict.get("time_slot", "Morning"),
            act_dict.get("start_time", "09:00"),
            act_dict.get("end_time", "11:00"),
            act_dict.get("location", ""),
            int(act_dict.get("duration_minutes", 90)),
            float(act_dict.get("estimated_cost", 0.0)),
            act_dict.get("currency", "USD"),
            act_dict.get("transportation_suggestion", ""),
            act_dict.get("practical_tips", ""),
            1 if act_dict.get("is_custom") else 0,
            int(act_dict.get("order_index", 0)),
            now,
            now
        )
    )
    conn.commit()
    cursor.execute("SELECT * FROM activities WHERE id = ?", (act_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)

def update_activity(activity_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    allowed = [
        "day_number", "date", "title", "description", "time_slot",
        "start_time", "end_time", "location", "duration_minutes",
        "estimated_cost", "currency", "transportation_suggestion",
        "practical_tips", "is_custom", "order_index"
    ]
    for k in allowed:
        if k in updates and updates[k] is not None:
            fields.append(f"{k} = ?")
            values.append(updates[k])
    if not fields:
        conn.close()
        return None

    now = datetime.utcnow().isoformat()
    fields.append("updated_at = ?")
    values.append(now)
    values.extend([activity_id, user_id])

    cursor.execute(f"UPDATE activities SET {', '.join(fields)} WHERE id = ? AND user_id = ?", values)
    conn.commit()
    cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_activity(activity_id: str, user_id: str) -> Optional[str]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT trip_id FROM activities WHERE id = ? AND user_id = ?", (activity_id, user_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    trip_id = row["trip_id"]
    cursor.execute("DELETE FROM activities WHERE id = ? AND user_id = ?", (activity_id, user_id))
    conn.commit()
    conn.close()
    return trip_id

def replace_day_activities(itinerary_id: str, trip_id: str, user_id: str, day_number: int, new_activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM activities WHERE itinerary_id = ? AND day_number = ? AND user_id = ?",
        (itinerary_id, day_number, user_id)
    )
    conn.commit()
    conn.close()

    inserted = []
    for act in new_activities:
        act["day_number"] = day_number
        created = create_activity(itinerary_id, trip_id, user_id, act)
        inserted.append(created)
    return inserted
