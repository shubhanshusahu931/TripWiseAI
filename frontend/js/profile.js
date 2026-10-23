/**
 * TripWise AI — Profile & Settings Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
  const session = await window.SupabaseAuth.getSession();
  if (!session) return;

  await loadProfile();
  initProfileForm();
  initConfigForm();
});

async function loadProfile() {
  try {
    const profile = await window.API.get("/api/v1/profile");

    document.getElementById("profile-email").value = profile.email || "";
    document.getElementById("profile-display-name").value = profile.display_name || "";
    document.getElementById("profile-currency").value = profile.preferred_currency || "USD";
    document.getElementById("profile-travel-style").value = profile.preferred_travel_style || "standard";
    document.getElementById("profile-home-city").value = profile.home_city || "";

    const avatarInitial = (profile.display_name || "T").charAt(0).toUpperCase();
    const avatarEl = document.getElementById("profile-avatar-large");
    if (avatarEl) avatarEl.textContent = avatarInitial;
  } catch (err) {
    console.error("Failed to load profile:", err);
    window.showToast("Could not fetch profile details.", "error");
  }
}

function initProfileForm() {
  const form = document.getElementById("profile-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = form.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner"></span> Saving...`;

    const payload = {
      display_name: document.getElementById("profile-display-name").value.trim(),
      preferred_currency: document.getElementById("profile-currency").value,
      preferred_travel_style: document.getElementById("profile-travel-style").value,
      home_city: document.getElementById("profile-home-city").value.trim()
    };

    try {
      await window.API.put("/api/v1/profile", payload);
      window.showToast("Profile updated successfully!", "success");

      // Update avatar letter
      const avatarInitial = (payload.display_name || "T").charAt(0).toUpperCase();
      const avatarEl = document.getElementById("profile-avatar-large");
      if (avatarEl) avatarEl.textContent = avatarInitial;
    } catch (err) {
      window.showToast(err.message || "Failed to update profile.", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Save Changes";
    }
  });

  const logoutBtn = document.getElementById("profile-logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      await window.SupabaseAuth.signOut();
      window.location.href = "login.html";
    });
  }
}

function initConfigForm() {
  // Allows user to view/update API and Supabase configuration in localStorage
  const apiUrlInput = document.getElementById("config-api-url");
  const supaUrlInput = document.getElementById("config-supabase-url");
  const supaKeyInput = document.getElementById("config-supabase-key");
  const configForm = document.getElementById("config-form");

  if (apiUrlInput) apiUrlInput.value = window.CONFIG.API_BASE_URL;
  if (supaUrlInput) supaUrlInput.value = window.CONFIG.SUPABASE_URL;
  if (supaKeyInput) supaKeyInput.value = window.CONFIG.SUPABASE_ANON_KEY;

  if (configForm) {
    configForm.addEventListener("submit", (e) => {
      e.preventDefault();
      localStorage.setItem("tripwise_api_url", apiUrlInput.value.trim());
      localStorage.setItem("tripwise_supabase_url", supaUrlInput.value.trim());
      localStorage.setItem("tripwise_supabase_anon_key", supaKeyInput.value.trim());
      window.showToast("Connection settings saved! Reloading...", "success");
      setTimeout(() => window.location.reload(), 800);
    });
  }
}
