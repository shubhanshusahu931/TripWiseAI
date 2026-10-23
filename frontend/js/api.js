/**
 * TripWise AI — Centralized API Client & UI Helpers
 */

const API = {
  getBaseUrl() {
    return window.CONFIG?.API_BASE_URL || "http://localhost:8000";
  },

  async request(endpoint, options = {}) {
    const token = await window.SupabaseAuth.getAccessToken();
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const url = `${this.getBaseUrl()}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401) {
        // Clear expired session and redirect to login if on protected page
        const isAuthPage = window.location.pathname.includes("login.html") || window.location.pathname.includes("signup.html");
        if (!isAuthPage) {
          window.SupabaseAuth.signOut();
          window.location.href = "login.html";
        }
        throw new Error("Session expired or unauthorized. Please log in.");
      }

      if (response.status === 204) {
        return null;
      }

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data?.detail || data?.message || "An error occurred during request.";
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: "GET" });
  },

  post(endpoint, body) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(body)
    });
  },

  put(endpoint, body) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(body)
    });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  }
};

window.API = API;

/**
 * Toast Notification System
 */
window.showToast = function(message, type = "info", duration = 4000) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: "✓",
    error: "✕",
    info: "ℹ"
  };

  const iconSpan = document.createElement("span");
  iconSpan.style.fontWeight = "bold";
  iconSpan.textContent = iconMap[type] || "•";

  const msgSpan = document.createElement("span");
  msgSpan.style.flex = "1";
  msgSpan.textContent = message;

  const closeBtn = document.createElement("button");
  closeBtn.className = "toast-close";
  closeBtn.innerHTML = "&times;";
  closeBtn.addEventListener("click", () => toast.remove());

  toast.appendChild(iconSpan);
  toast.appendChild(msgSpan);
  toast.appendChild(closeBtn);
  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) {
      toast.remove();
    }
  }, duration);
};

/**
 * Safe DOM Text / Escaping Helper
 */
window.escapeHtml = function(unsafe) {
  if (unsafe === null || unsafe === undefined) return "";
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};
