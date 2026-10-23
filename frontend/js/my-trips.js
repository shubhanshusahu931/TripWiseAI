/**
 * TripWise AI — My Trips Page Controller
 */

let allTrips = [];
let deleteTargetTripId = null;

document.addEventListener("DOMContentLoaded", async () => {
  const session = await window.SupabaseAuth.getSession();
  if (!session) return;

  initFilters();
  initDeleteModal();
  await fetchTrips();
});

function initFilters() {
  const searchInput = document.getElementById("trip-search-input");
  const statusFilter = document.getElementById("trip-status-filter");
  const sortFilter = document.getElementById("trip-sort-filter");

  let debounceTimer;
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => fetchTrips(), 300);
    });
  }

  if (statusFilter) {
    statusFilter.addEventListener("change", () => fetchTrips());
  }

  if (sortFilter) {
    sortFilter.addEventListener("change", () => fetchTrips());
  }
}

async function fetchTrips() {
  const search = document.getElementById("trip-search-input")?.value.trim() || "";
  const status = document.getElementById("trip-status-filter")?.value || "all";
  const sortBy = document.getElementById("trip-sort-filter")?.value || "newest";

  const container = document.getElementById("my-trips-grid");
  const emptyBox = document.getElementById("my-trips-empty");

  try {
    let query = `/api/v1/trips?sort_by=${sortBy}`;
    if (search) query += `&search=${encodeURIComponent(search)}`;
    if (status && status !== "all") query += `&status=${status}`;

    const trips = await window.API.get(query);
    allTrips = trips;

    if (!trips || trips.length === 0) {
      if (container) container.innerHTML = "";
      if (emptyBox) emptyBox.style.display = "block";
    } else {
      if (emptyBox) emptyBox.style.display = "none";
      if (container) {
        container.innerHTML = "";
        trips.forEach(t => {
          container.appendChild(createTripCard(t));
        });
      }
    }
  } catch (err) {
    console.error("Failed to fetch trips:", err);
    window.showToast("Failed to load trips.", "error");
  }
}

function createTripCard(trip) {
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
        <span>👥 ${window.escapeHtml(trip.num_travelers)} traveler(s)</span>
      </div>
    </div>
    <div class="trip-card-actions">
      <a href="itinerary.html?id=${trip.id}" class="btn btn-primary btn-sm" style="flex: 1;">View Details</a>
      <button class="trip-action-btn" data-action="duplicate" data-id="${trip.id}" title="Duplicate Trip">📋 Duplicate</button>
      <button class="trip-action-btn delete" data-action="delete" data-id="${trip.id}" title="Delete Trip">🗑️</button>
    </div>
  `;

  // Actions
  card.querySelector("[data-action='duplicate']").addEventListener("click", async () => {
    try {
      await window.API.post(`/api/v1/trips/${trip.id}/duplicate`);
      window.showToast("Trip duplicated successfully!", "success");
      await fetchTrips();
    } catch (e) {
      window.showToast(e.message, "error");
    }
  });

  card.querySelector("[data-action='delete']").addEventListener("click", () => {
    deleteTargetTripId = trip.id;
    document.getElementById("delete-trip-name").textContent = trip.title;
    document.getElementById("delete-trip-modal").classList.add("show");
  });

  return card;
}

function initDeleteModal() {
  const modal = document.getElementById("delete-trip-modal");
  const confirmBtn = document.getElementById("confirm-delete-trip-btn");

  if (confirmBtn) {
    confirmBtn.addEventListener("click", async () => {
      if (!deleteTargetTripId) return;
      confirmBtn.disabled = true;
      try {
        await window.API.delete(`/api/v1/trips/${deleteTargetTripId}`);
        window.showToast("Trip deleted.", "info");
        modal.classList.remove("show");
        deleteTargetTripId = null;
        await fetchTrips();
      } catch (err) {
        window.showToast(err.message, "error");
      } finally {
        confirmBtn.disabled = false;
      }
    });
  }

  document.querySelectorAll(".modal-close-btn, .modal-cancel-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (modal) modal.classList.remove("show");
    });
  });
}
