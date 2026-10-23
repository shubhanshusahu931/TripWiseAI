/**
 * TripWise AI — Frontend Configuration
 * Manages API endpoints and Supabase credentials
 */

const CONFIG = {
  // If served directly from FastAPI (e.g. port 8000), use origin; otherwise default to localhost:8000
  API_BASE_URL: window.location.port === "8000" 
    ? window.location.origin 
    : (localStorage.getItem("tripwise_api_url") || "http://localhost:8000"),

  // Supabase Credentials (public browser keys)
  // Replace these with your Supabase project keys if using live Supabase Auth
  SUPABASE_URL: localStorage.getItem("tripwise_supabase_url") || "",
  SUPABASE_ANON_KEY: localStorage.getItem("tripwise_supabase_anon_key") || "",

  // App defaults
  DEFAULT_CURRENCY: "USD",
  CURRENCIES: ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD"]
};

window.CONFIG = CONFIG;
