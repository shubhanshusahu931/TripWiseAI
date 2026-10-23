/**
 * TripWise AI — Dashboard Controller
 */

document.addEventListener("DOMContentLoaded", async () => {
  const session = await window.SupabaseAuth.getSession();
  if (!session) return;

  // Set greeting with user name
  const userNameElem = document.getElementById("user-greeting-name");
  if (userNameElem) {
    const name = session.user.user_metadata?.full_name || session.user.email.split("@")[0];
    userNameElem.textContent = name;
  }

  await loadDashboardData();
});

async function loadDashboardData() {
  const statsContainer = document.getElementById("dashboard-stats");
  const tripsContainer = document.getElementById("recent-trips-container");
  const emptyState = document.getElementById("dashboard-empty-state");

  try {
    const trips = await window.API.get("/api/v1/trips");

    // Compute real metrics
    const totalTrips = trips.length;
    const today = new Date().toISOString().split("T")[0];
    const upcomingTrips = trips.filter(t => t.start_date >= today).length;
    const totalBudget = trips.reduce((sum, t) => sum + (parseFloat(t.total_budget) || 0), 0);
    const uniqueDestinations = new Set(trips.map(t => t.destination.toLowerCase().trim())).size;

    // Update KPI counters
    document.getElementById("stat-total-trips").textContent = totalTrips;
    document.getElementById("stat-upcoming-trips").textContent = upcomingTrips;
    document.getElementById("stat-total-budget").textContent = `$${Math.round(totalBudget).toLocaleString()}`;
    document.getElementById("stat-destinations").textContent = uniqueDestinations;

    if (totalTrips === 0) {
      if (tripsContainer) tripsContainer.style.display = "none";
      if (emptyState) emptyState.style.display = "block";
    } else {
      if (emptyState) emptyState.style.display = "none";
      if (tripsContainer) {
        tripsContainer.style.display = "grid";
        tripsContainer.innerHTML = "";
        
        // Show up to 6 recent trips
        const recent = trips.slice(0, 6);
        recent.forEach(trip => {
          tripsContainer.appendChild(createTripCardElement(trip));
        });
      }
    }
  } catch (err) {
    console.error("Failed to load dashboard:", err);
    window.showToast("Could not load dashboard trips. Please ensure backend is running.", "error");
  }
}

function createTripCardElement(trip) {
  const card = document.createElement("div");
  card.className = "trip-card";

  const statusClass = `badge-${trip.status || 'planning'}`;
  const coverUrl = trip.cover_image_url || "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=800&q=80";

  card.innerHTML = `
    <div class="trip-card-image-wrap">
      <img src="${window.escapeHtml(coverUrl)}" alt="${window.escapeHtml(trip.destination)}" class="trip-card-image" loading="lazy">
      <div class="trip-card-badges">
        <span class="badge ${statusClass}">${window.escapeHtml(trip.status || 'Planning')}</span>
        <span class="badge" style="background: rgba(0,0,0,0.6); color: white;">${window.escapeHtml(trip.currency)} ${Math.round(trip.total_budget).toLocaleString()}</span>
      </div>
    </div>
    <div class="trip-card-content">
      <h3 class="trip-card-title">${window.escapeHtml(trip.title)}</h3>
      <div class="trip-card-dest">
        📍 <span>${window.escapeHtml(trip.destination)}</span>
      </div>
      <div class="trip-card-meta">
        <span>📅 ${window.escapeHtml(trip.start_date)} - ${window.escapeHtml(trip.end_date)}</span>
        <span>👥 ${window.escapeHtml(trip.num_travelers)} ${trip.num_travelers > 1 ? 'travelers' : 'traveler'}</span>
      </div>
    </div>
    <div class="trip-card-actions">
      <a href="itinerary.html?id=${trip.id}" class="btn btn-primary btn-sm" style="flex: 1;">View Itinerary</a>
      <button class="trip-action-btn" data-action="duplicate" data-id="${trip.id}" title="Duplicate Trip">📋</button>
      <button class="trip-action-btn delete" data-action="delete" data-id="${trip.id}" title="Delete Trip">🗑️</button>
    </div>
  `;

  // Attach event listeners
  const dupBtn = card.querySelector("[data-action='duplicate']");
  const delBtn = card.querySelector("[data-action='delete']");

  dupBtn.addEventListener("click", async () => {
    dupBtn.disabled = true;
    try {
      await window.API.post(`/api/v1/trips/${trip.id}/duplicate`);
      window.showToast("Trip duplicated!", "success");
      await loadDashboardData();
    } catch (e) {
      window.showToast(e.message, "error");
      dupBtn.disabled = false;
    }
  });

  delBtn.addEventListener("click", async () => {
    if (confirm(`Are you sure you want to delete "${trip.title}"?`)) {
      try {
        await window.API.delete(`/api/v1/trips/${trip.id}`);
        window.showToast("Trip deleted.", "info");
        await loadDashboardData();
      } catch (e) {
        window.showToast(e.message, "error");
      }
    }
  });

  return card;
}
