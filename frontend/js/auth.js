/**
 * TripWise AI — Auth Management & Navigation
 */

document.addEventListener("DOMContentLoaded", async () => {
  const isLoginPage = window.location.pathname.includes("login.html");
  const isSignupPage = window.location.pathname.includes("signup.html");
  const isIndexPage = window.location.pathname.endsWith("index.html") || window.location.pathname.endsWith("/");

  const session = await window.SupabaseAuth.getSession();

  // If on login or signup and already logged in, redirect to dashboard
  if ((isLoginPage || isSignupPage) && session) {
    window.location.href = "dashboard.html";
    return;
  }

  // If on a protected page and not logged in, redirect to login
  const isProtectedPage = ["dashboard.html", "create-trip.html", "itinerary.html", "my-trips.html", "profile.html"]
    .some(p => window.location.pathname.includes(p));

  if (isProtectedPage && !session) {
    window.location.href = "login.html";
    return;
  }

  // Initialize Navbar UI (User Avatar, Logout, Mobile Menu)
  initNavbar(session);

  // Initialize Login Form
  if (isLoginPage) {
    initLoginForm();
  }

  // Initialize Signup Form
  if (isSignupPage) {
    initSignupForm();
  }
});

function initNavbar(session) {
  const userNavContainer = document.getElementById("navbar-user-section");
  const menuToggle = document.getElementById("mobile-menu-toggle");
  const navLinks = document.getElementById("nav-links");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }

  if (userNavContainer) {
    if (session && session.user) {
      const email = session.user.email || "traveler@tripwise.ai";
      const name = session.user.user_metadata?.full_name || email.split("@")[0];
      const initial = name.charAt(0).toUpperCase();

      userNavContainer.innerHTML = `
        <div class="user-menu-wrapper">
          <button class="user-avatar-btn" id="user-menu-btn" type="button" aria-haspopup="true">
            <div class="avatar-circle">${window.escapeHtml(initial)}</div>
            <span class="user-name-label">${window.escapeHtml(name)}</span>
            <span style="font-size: 0.75rem; color: #94A3B8;">▼</span>
          </button>
          <div class="dropdown-menu" id="user-dropdown">
            <a href="profile.html" class="dropdown-item">👤 Profile & Settings</a>
            <a href="my-trips.html" class="dropdown-item">✈️ My Trips</a>
            <div class="dropdown-divider"></div>
            <button class="dropdown-item" id="logout-btn" style="color: var(--color-rose);">🚪 Log Out</button>
          </div>
        </div>
      `;

      const menuBtn = document.getElementById("user-menu-btn");
      const dropdown = document.getElementById("user-dropdown");
      const logoutBtn = document.getElementById("logout-btn");

      if (menuBtn && dropdown) {
        menuBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          dropdown.classList.toggle("show");
        });

        document.addEventListener("click", () => {
          dropdown.classList.remove("show");
        });
      }

      if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
          await window.SupabaseAuth.signOut();
          window.location.href = "login.html";
        });
      }
    } else {
      userNavContainer.innerHTML = `
        <a href="login.html" class="btn btn-secondary btn-sm">Log In</a>
        <a href="signup.html" class="btn btn-primary btn-sm">Sign Up Free</a>
      `;
    }
  }
}

function initLoginForm() {
  const form = document.getElementById("login-form");
  const demoBtn = document.getElementById("demo-login-btn");
  const toggleBtn = document.getElementById("toggle-password");
  const pwdInput = document.getElementById("password");

  if (toggleBtn && pwdInput) {
    toggleBtn.addEventListener("click", () => {
      const type = pwdInput.type === "password" ? "text" : "password";
      pwdInput.type = type;
      toggleBtn.textContent = type === "password" ? "👁️" : "🙈";
    });
  }

  if (demoBtn) {
    demoBtn.addEventListener("click", async () => {
      demoBtn.disabled = true;
      demoBtn.textContent = "Logging into Demo Account...";
      try {
        await window.SupabaseAuth.signIn("demo@tripwise.ai", "DemoPassword123!");
        window.showToast("Signed in as Demo User!", "success");
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 500);
      } catch (err) {
        window.showToast(err.message, "error");
        demoBtn.disabled = false;
        demoBtn.textContent = "⚡ Quick Try: Demo Account";
      }
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value.trim();
      const password = pwdInput.value;
      const submitBtn = form.querySelector("button[type='submit']");

      if (!email || !password) {
        window.showToast("Please enter email and password.", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner"></span> Signing in...`;

      try {
        const { data, error } = await window.SupabaseAuth.signIn(email, password);
        if (error) throw error;
        window.showToast("Welcome back to TripWise!", "success");
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 600);
      } catch (err) {
        window.showToast(err.message || "Invalid credentials.", "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Log In";
      }
    });
  }
}

function initSignupForm() {
  const form = document.getElementById("signup-form");
  const demoBtn = document.getElementById("demo-login-btn");

  if (demoBtn) {
    demoBtn.addEventListener("click", async () => {
      await window.SupabaseAuth.signIn("demo@tripwise.ai", "DemoPassword123!");
      window.location.href = "dashboard.html";
    });
  }

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fullName = document.getElementById("fullName").value.trim();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      const confirmPassword = document.getElementById("confirmPassword").value;
      const submitBtn = form.querySelector("button[type='submit']");

      if (password !== confirmPassword) {
        window.showToast("Passwords do not match.", "error");
        return;
      }

      if (password.length < 6) {
        window.showToast("Password must be at least 6 characters.", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner"></span> Creating Account...`;

      try {
        const { data, error } = await window.SupabaseAuth.signUp(email, password, fullName);
        if (error) throw error;
        window.showToast("Account created successfully!", "success");
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 600);
      } catch (err) {
        window.showToast(err.message || "Failed to create account.", "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Create Account";
      }
    });
  }
}
