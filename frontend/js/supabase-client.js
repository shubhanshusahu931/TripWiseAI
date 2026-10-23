/**
 * TripWise AI — Supabase Client Wrapper
 * Handles Supabase Auth and Session Persistence
 */

(function() {
  let supabaseClient = null;

  // Initialize Supabase if keys and SDK are present
  if (window.supabase && window.CONFIG && window.CONFIG.SUPABASE_URL && window.CONFIG.SUPABASE_ANON_KEY) {
    try {
      supabaseClient = window.supabase.createClient(
        window.CONFIG.SUPABASE_URL,
        window.CONFIG.SUPABASE_ANON_KEY
      );
    } catch (err) {
      console.warn("Failed to initialize Supabase client:", err);
    }
  }

  // Fallback / Demo Auth Provider for Offline & Rapid Evaluation
  const DemoAuthProvider = {
    async signInWithPassword({ email, password }) {
      if (!email || !password) {
        return { data: null, error: { message: "Email and password are required." } };
      }
      const user = {
        id: "00000000-0000-0000-0000-000000000001",
        email: email,
        user_metadata: { full_name: email.split("@")[0] }
      };
      const session = {
        access_token: "demo-token",
        user: user
      };
      localStorage.setItem("tripwise_session", JSON.stringify(session));
      return { data: { user, session }, error: null };
    },

    async signUp({ email, password, options }) {
      if (!email || !password) {
        return { data: null, error: { message: "Email and password are required." } };
      }
      const user = {
        id: "00000000-0000-0000-0000-000000000001",
        email: email,
        user_metadata: options?.data || { full_name: email.split("@")[0] }
      };
      const session = {
        access_token: "demo-token",
        user: user
      };
      localStorage.setItem("tripwise_session", JSON.stringify(session));
      return { data: { user, session }, error: null };
    },

    async signOut() {
      localStorage.removeItem("tripwise_session");
      return { error: null };
    },

    async getSession() {
      const raw = localStorage.getItem("tripwise_session");
      if (raw) {
        try {
          return { data: { session: JSON.parse(raw) }, error: null };
        } catch (e) {
          localStorage.removeItem("tripwise_session");
        }
      }
      return { data: { session: null }, error: null };
    }
  };

  window.SupabaseAuth = {
    getClient() {
      return supabaseClient;
    },

    async signIn(email, password) {
      if (supabaseClient) {
        const res = await supabaseClient.auth.signInWithPassword({ email, password });
        if (!res.error && res.data.session) {
          localStorage.setItem("tripwise_session", JSON.stringify(res.data.session));
        }
        return res;
      }
      return DemoAuthProvider.signInWithPassword({ email, password });
    },

    async signUp(email, password, fullName) {
      if (supabaseClient) {
        const res = await supabaseClient.auth.signUp({
          email,
          password,
          options: { data: { full_name: fullName } }
        });
        if (!res.error && res.data.session) {
          localStorage.setItem("tripwise_session", JSON.stringify(res.data.session));
        }
        return res;
      }
      return DemoAuthProvider.signUp({ email, password, options: { data: { full_name: fullName } } });
    },

    async signOut() {
      if (supabaseClient) {
        await supabaseClient.auth.signOut();
      }
      return DemoAuthProvider.signOut();
    },

    async getSession() {
      if (supabaseClient) {
        const res = await supabaseClient.auth.getSession();
        if (res.data?.session) {
          return res.data.session;
        }
      }
      const res = await DemoAuthProvider.getSession();
      return res.data?.session || null;
    },

    async getAccessToken() {
      const session = await this.getSession();
      return session ? session.access_token : null;
    }
  };
})();
