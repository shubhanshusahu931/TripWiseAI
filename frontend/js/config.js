/**
 * TripWise AI — Frontend Configuration
 * Manages API endpoints and Supabase credentials
 */

const CONFIG = {
  // Point strictly to your live FastAPI backend URL hosted on Render
  API_BASE_URL: "https://tripwiseai-e6an.onrender.com",

  // Supabase Credentials (public browser keys)
  // Replace these blank strings with your real project keys if you don't want to type them in the UI
  SUPABASE_URL: localStorage.getItem("tripwise_supabase_url") || "",
  SUPABASE_ANON_KEY: localStorage.getItem("tripwise_supabase_anon_key") || "",

  // App defaults
  DEFAULT_CURRENCY: "USD",
  CURRENCIES: ["USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD"]
};

window.CONFIG = CONFIG;
