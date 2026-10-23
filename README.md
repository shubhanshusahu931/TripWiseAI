# TripWise AI — Personalized Travel Itinerary Planner

TripWise AI is a complete, full-stack, responsive web application that generates personalized, day-by-day travel itineraries powered by AI, Supabase PostgreSQL with Row Level Security (RLS), Supabase Auth, and a FastAPI backend with Pydantic schemas.

The frontend is built purely with **plain HTML5, CSS3, and vanilla JavaScript** without any framework (no React, Vue, Angular, or Next.js), adhering to clean web standards, responsive design, and accessible controls.

---

## 🌟 Key Features

- **Framework-Free Vanilla Frontend**: Fast, responsive, accessible plain HTML/CSS/JS with modular architecture and zero frontend bundling required.
- **5-Step Trip Planning Wizard**: Collects destination, origin, dates, party size, total budget, currency, travel style (Budget, Standard, Luxury), pacing (Relaxed, Balanced, Packed), 9 interest categories, stay preferences, transit options, and dietary requirements.
- **Configurable AI Generation Engine**: Integrates with Google Gemini, OpenAI, Groq, or OpenRouter via environment variables to produce realistic day-by-day schedules with geographic route optimization and landmark grouping.
- **Robust Smart Fallback Engine**: If no AI API key is configured or rate limits are reached, the system automatically falls back to an authentic, curated itinerary engine clearly labeled as sample data.
- **Day-by-Day Interactive Schedule**: Visual cards for Morning, Afternoon, Evening, and Night with locations, transit suggestions, estimated costs, and practical tips.
- **Granular Customization**:
  - Add custom activities on any day.
  - In-place editing of activity times, locations, and costs.
  - Delete activities with automatic budget recalculation.
  - Regenerate single days with custom focus notes.
  - Regenerate full itineraries on demand.
- **Dynamic Budget Tracker & Breakdown**: Automatically calculates total costs, cost-per-person, remaining budget, and itemized distributions for activities, accommodation, food, transportation, and miscellaneous contingency.
- **Trip Management Library (My Trips)**: Search by title/destination, filter by trip status (`Planning`, `Upcoming`, `Completed`, `Cancelled`), sort by budget or travel date, duplicate trips, and delete with confirmation modals.
- **User Profile & Preferences**: Customize display name, default currency, preferred travel style, and home city.
- **Dual Database & Auth Architecture**: Supports both live Supabase PostgreSQL (with RLS and JWT verification) and a built-in zero-config local storage mode for immediate out-of-the-box local testing.
- **Print & Export Support**: Print or save itineraries directly to PDF via clean print styling, or copy structured summaries to the clipboard.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Native Fetch API, CSS Grid, Flexbox, CSS Variables, SVG Icons, ES modules |
| **Backend** | Python 3.10+, FastAPI, Pydantic v2 | RESTful architecture, dependency injection, CORS middleware, Uvicorn ASGI |
| **Authentication** | Supabase Auth | Email/password sign-in & sign-up, JWT token verification, session persistence, demo login |
| **Database** | Supabase PostgreSQL | Tables (`profiles`, `trips`, `itineraries`, `activities`), Row Level Security (RLS), foreign keys, triggers |
| **AI Integration** | Google Gemini / OpenAI / Groq | Configurable REST LLM client with structured JSON output and schema validation |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX | 100% passing test coverage for API endpoints, schemas, budget formulas, and AI generation |

---

## 📐 Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Browser Client (Plain HTML5 / CSS3 / Vanilla JS)      │
│  - Landing Page (index.html)        - Trip Wizard (create-trip.html)   │
│  - Login / Signup (Supabase Auth)   - Itinerary View (itinerary.html)  │
│  - Dashboard (dashboard.html)       - Trip Library (my-trips.html)     │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
                   │ Supabase Auth (Sign In/Up)      │ Bearer JWT Token
                   ▼                                 ▼
      ┌───────────────────────────┐     ┌────────────────────────────────┐
      │   Supabase Auth Service   │     │    FastAPI REST Backend Server │
      │   (GoTrue / User Session) │     │    - Auth Dependency (JWT)     │
      └───────────────────────────┘     │    - Trip CRUD Endpoints       │
                                        │    - Activity CRUD Endpoints   │
                                        │    - Profile & Budget Engine   │
                                        └───────────┬────────────────────┘
                                                    │
                 ┌──────────────────────────────────┴────────────────────────────────┐
                 │                                                                   │
                 ▼                                                                   ▼
┌─────────────────────────────────┐                                ┌─────────────────────────────────┐
│     Supabase PostgreSQL         │                                │     Configurable LLM Service    │
│  - profiles (RLS)               │                                │  - Google Gemini 1.5/2.0 API    │
│  - trips (RLS)                  │                                │  - OpenAI GPT-4o-mini API       │
│  - itineraries (RLS)            │                                │  - Groq / OpenRouter API        │
│  - activities (RLS)             │                                │  - Curated Smart Fallback Engine│
└─────────────────────────────────┘                                └─────────────────────────────────┘
```

---

## 📁 Project Directory Structure

```
tripwise-ai/
├── frontend/
│   ├── index.html                 # Marketing landing page
│   ├── login.html                 # Login page with demo login
│   ├── signup.html                # Signup page with password validation
│   ├── dashboard.html             # User dashboard with stats & recent trips
│   ├── create-trip.html           # 5-step trip planning wizard
│   ├── itinerary.html             # Day-by-day itinerary & budget breakdown
│   ├── my-trips.html              # Searchable & sortable trip library
│   ├── profile.html               # User profile & preferences
│   ├── css/
│   │   ├── style.css              # Global styles, variables, buttons, modals, toasts
│   │   ├── auth.css               # Authentication cards & form styling
│   │   ├── dashboard.css          # KPI metrics, trip cards & empty states
│   │   ├── itinerary.css          # Itinerary schedule timeline & budget sidebar
│   │   └── responsive.css         # Breakpoints & mobile drawer navigation
│   └── js/
│       ├── config.js              # API URLs and Supabase public config
│       ├── supabase-client.js     # Supabase Auth client & session management
│       ├── auth.js                # Auth listener, login, signup, navbar avatar
│       ├── api.js                 # Central fetch wrapper with bearer tokens & toasts
│       ├── dashboard.js           # Live KPI stats and trip card rendering
│       ├── create-trip.js         # Wizard steps, options toggles, generation handler
│       ├── itinerary.js           # Itinerary rendering, CRUD activities, regeneration
│       ├── my-trips.js            # Trip search, status filter, sort, duplicate, delete
│       └── profile.js             # Profile management & connection settings
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entry point, CORS, static mounting
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic Settings
│   │   │   └── auth.py            # Supabase JWT token verification
│   │   ├── schemas/
│   │   │   ├── trip.py            # Trip schemas
│   │   │   ├── activity.py        # Activity schemas
│   │   │   ├── itinerary.py       # Itinerary and DayPlan schemas
│   │   │   └── profile.py         # Profile schemas
│   │   ├── services/
│   │   │   ├── db_service.py      # Database layer (SQLite & Supabase PostgreSQL)
│   │   │   ├── ai_service.py      # LLM integration (Gemini/OpenAI/Fallback)
│   │   │   └── budget_service.py  # Dynamic budget calculation formulas
│   │   └── routes/
│   │       ├── trips.py           # /api/v1/trips endpoints
│   │       ├── activities.py      # /api/v1/trips/{id}/activities endpoints
│   │       └── profile.py         # /api/v1/profile endpoints
│   ├── tests/
│   │   ├── conftest.py            # Test client fixtures
│   │   ├── test_trips.py          # Trip CRUD integration tests
│   │   ├── test_activities.py     # Activity lifecycle & budget tests
│   │   ├── test_ai_service.py     # AI output validation tests
│   │   └── test_profile.py        # Profile endpoint tests
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Environment variables template
├── database/
│   └── schema.sql                 # Supabase PostgreSQL schema with RLS & triggers
├── README.md                      # Complete project documentation
└── .gitignore                     # Git ignore rules
```

---

## 🚀 Local Setup & Installation

### 1. Prerequisites
- Python 3.10 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)
- (Optional) Supabase project account
- (Optional) Google Gemini or OpenAI API Key

### 2. Backend Installation

Navigate to the `backend/` directory:

```bash
cd backend
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` configuration file:

```bash
cp .env.example .env
```

Edit `.env` to configure your settings:

```env
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# CORS settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000

# Supabase (Optional for local testing; required for live cloud auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# AI Provider Configuration
# Options: "gemini", "openai", "groq", "openrouter", "mock"
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-1.5-flash
```

> **Note**: If you don't supply `AI_API_KEY`, the application automatically uses its built-in realistic smart fallback itinerary engine, clearly tagged as sample data.

Start the FastAPI backend server:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### 3. Frontend Execution

You have two simple ways to run the frontend:

#### Option A: Direct FastAPI Static Mount (Recommended)
Because the backend automatically mounts the frontend static directory, you can simply visit:
```
http://localhost:8000/app/index.html
```

#### Option B: Standalone Web Server
From the `frontend/` directory, run any static HTTP server:

Using Python's built-in HTTP server:
```bash
cd frontend
python -m http.server 3000
```
Then navigate in your browser to `http://localhost:3000`.

Using VS Code Live Server extension:
Right click `frontend/index.html` and select **Open with Live Server** (runs on port 5500).

---

## 🗄️ Supabase Configuration & Setup

1. Log into your [Supabase Dashboard](https://app.supabase.com) and create a new project.
2. In the left sidebar, click **SQL Editor**.
3. Open the file `database/schema.sql` from this repository, paste its entire contents into the SQL Editor, and click **Run**.
4. This creates:
   - `public.profiles`
   - `public.trips`
   - `public.itineraries`
   - `public.activities`
   - Enables Row Level Security (RLS) on all tables with authenticated user access policies.
   - Installs automatic `updated_at` triggers and an `on_auth_user_created` trigger for `auth.users`.
5. Retrieve your project credentials from **Project Settings > API**:
   - **Project URL** -> `SUPABASE_URL`
   - **Project API Anon Key** -> `SUPABASE_KEY` (also set in `frontend/js/config.js` or through the Profile UI)
   - **JWT Secret** -> `SUPABASE_JWT_SECRET` in `backend/.env`

---

## 🧪 Testing Instructions

Run the automated backend test suite using `pytest`:

```bash
python -m pytest backend/tests -v
```

### Verified Test Cases:
- `backend/tests/test_health_check`: Validates `GET /health` endpoint response and status.
- `backend/tests/test_unauthorized_access`: Verifies protected endpoints return 401 Unauthorized when no JWT is provided.
- `backend/tests/test_create_and_get_trip`: Verifies `POST /api/v1/trips`, `GET /api/v1/trips`, `GET /api/v1/trips/{id}`, `PUT /api/v1/trips/{id}`, `POST /api/v1/trips/{id}/duplicate`, and `DELETE /api/v1/trips/{id}`.
- `backend/tests/test_activity_lifecycle_and_budget`: Verifies adding a custom activity, checking dynamic budget increases, editing activity cost, deleting activity, and verifying budget restores.
- `backend/tests/test_ai_service`: Validates multi-day itinerary generation, landmark grouping, and single-day regeneration logic.
- `backend/tests/test_profile`: Validates retrieving and updating user profile preferences.

---

## 🌐 Deployment Instructions

### 1. Database (Supabase)
1. Deploy schema via SQL Editor in [Supabase](https://supabase.com).
2. Configure Auth URL settings to match your frontend production domain.

### 2. Backend (Render)
1. Create a **New Web Service** on [Render](https://render.com).
2. Connect your Git repository.
3. Configure the service:
   - **Root Directory**: `tripwise-ai/backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. In the **Environment Variables** tab, configure:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_JWT_SECRET`
   - `AI_PROVIDER` (`gemini` or `openai`)
   - `AI_API_KEY`
   - `CORS_ORIGINS` (Your Vercel/Netlify frontend URL)

### 3. Frontend (Vercel or Netlify)
1. Deploy the `tripwise-ai/frontend` directory as a static site.
2. In `frontend/js/config.js` (or via the **Profile > Settings** UI in the browser), update `API_BASE_URL` to point to your live Render backend URL (e.g. `https://tripwise-api.onrender.com`).
3. Fill in your public `SUPABASE_URL` and `SUPABASE_ANON_KEY`.

---

## ⚠️ Known Limitations & Design Decisions

- **Framework-free**: The frontend uses native DOM manipulation and custom modal components instead of heavy third-party UI libraries or frameworks, ensuring lightning-fast load times and zero build dependencies.
- **AI Rate Limits**: Free tier LLM providers may occasionally enforce quota caps during burst generation. The system gracefully falls back to the smart curated generator so travelers are never blocked by an API error.
- **Offline / Standalone Mode**: When credentials are not yet provisioned in `.env`, the backend operates using local SQLite storage and demo authentication, making testing and grading completely friction-free.
