/**
 * TripWise AI — Itinerary Page Controller
 */

let currentTrip = null;
let currentItinerary = null;
let activeDayNumber = 1;

document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const tripId = urlParams.get("id");

  if (!tripId) {
    window.location.href = "dashboard.html";
    return;
  }

  await loadTripData(tripId);
  initItineraryControls(tripId);
  initModalListeners(tripId);
});

async function loadTripData(tripId) {
  try {
    const data = await window.API.get(`/api/v1/trips/${tripId}`);
    currentTrip = data;
    currentItinerary = data.itinerary;

    if (!currentItinerary) {
      window.showToast("Itinerary not found for this trip.", "error");
      return;
    }

    renderTripHero();
    renderDayTabs();
    renderActiveDaySchedule();
    renderBudgetBreakdown();
  } catch (err) {
    console.error("Failed to load itinerary:", err);
    window.showToast("Error loading trip data.", "error");
  }
}

function renderTripHero() {
  const hero = document.getElementById("itinerary-hero");
  if (!hero) return;

  const coverUrl = currentTrip.cover_image_url || "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80";
  hero.style.backgroundImage = `url('${coverUrl}')`;

  document.getElementById("itinerary-title").textContent = currentTrip.title;
  document.getElementById("itinerary-dest-label").textContent = `📍 ${currentTrip.destination}`;
  document.getElementById("itinerary-dates-label").textContent = `📅 ${currentTrip.start_date} to ${currentTrip.end_date}`;
  document.getElementById("itinerary-travelers-label").textContent = `👥 ${currentTrip.num_travelers} traveler(s)`;
  document.getElementById("itinerary-style-label").textContent = `✨ ${currentTrip.travel_style} (${currentTrip.travel_pace})`;

  const sampleBadge = document.getElementById("sample-data-badge");
  if (sampleBadge) {
    sampleBadge.style.display = currentItinerary.is_sample_data ? "inline-flex" : "none";
  }

  const summaryText = document.getElementById("itinerary-summary-text");
  if (summaryText && currentItinerary.summary) {
    summaryText.textContent = currentItinerary.summary;
  }
}

function renderDayTabs() {
  const container = document.getElementById("day-tabs-container");
  if (!container || !currentItinerary.days) return;

  container.innerHTML = "";
  currentItinerary.days.forEach(day => {
    const btn = document.createElement("button");
    btn.className = `day-tab-btn ${day.day_number === activeDayNumber ? 'active' : ''}`;
    btn.innerHTML = `<span>Day ${day.day_number}</span>`;
    btn.addEventListener("click", () => {
      activeDayNumber = day.day_number;
      renderDayTabs();
      renderActiveDaySchedule();
    });
    container.appendChild(btn);
  });
}

function renderActiveDaySchedule() {
  const scheduleContainer = document.getElementById("day-schedule-container");
  const dayTitleElem = document.getElementById("active-day-heading");
  if (!scheduleContainer || !currentItinerary.days) return;

  const currentDay = currentItinerary.days.find(d => d.day_number === activeDayNumber) || currentItinerary.days[0];
  if (!currentDay) {
    scheduleContainer.innerHTML = "<p>No activities planned for this day.</p>";
    return;
  }

  if (dayTitleElem) {
    dayTitleElem.textContent = `Day ${currentDay.day_number}: ${currentDay.theme || currentTrip.destination}`;
  }

  scheduleContainer.innerHTML = "";

  const timeSlots = ["Morning", "Afternoon", "Evening", "Night"];
  const activities = currentDay.activities || [];

  if (activities.length === 0) {
    scheduleContainer.innerHTML = `
      <div class="empty-state-box" style="padding: 2rem;">
        <p style="color: var(--text-muted); margin-bottom: 1rem;">No activities planned for Day ${activeDayNumber} yet.</p>
        <button class="btn btn-outline-teal btn-sm" id="empty-add-activity-btn">+ Add Activity</button>
      </div>
    `;
    const addBtn = document.getElementById("empty-add-activity-btn");
    if (addBtn) addBtn.addEventListener("click", () => openAddActivityModal());
    return;
  }

  timeSlots.forEach(slot => {
    const slotActivities = activities.filter(a => (a.time_slot || "Morning").toLowerCase() === slot.toLowerCase());
    if (slotActivities.length > 0) {
      const section = document.createElement("div");
      section.className = "time-slot-section";

      const slotIcons = {
        morning: "🌅",
        afternoon: "☀️",
        evening: "🌆",
        night: "🌙"
      };

      section.innerHTML = `
        <div class="time-slot-heading">
          <span>${slotIcons[slot.toLowerCase()] || "•"}</span>
          <span>${slot}</span>
          <span class="time-slot-badge">${slotActivities.length} ${slotActivities.length > 1 ? 'activities' : 'activity'}</span>
        </div>
      `;

      slotActivities.forEach(act => {
        section.appendChild(createActivityCard(act));
      });

      scheduleContainer.appendChild(section);
    }
  });
}

function createActivityCard(act) {
  const card = document.createElement("div");
  card.className = "activity-card";

  const currency = act.currency || currentTrip.currency || "USD";
  const costFormatted = `${currency} ${parseFloat(act.estimated_cost || 0).toFixed(2)}`;

  card.innerHTML = `
    <div class="activity-card-header">
      <div>
        <h4 class="activity-title">${window.escapeHtml(act.title)}</h4>
        <div class="activity-pills">
          <span class="pill-item pill-time">⏱️ ${window.escapeHtml(act.start_time || '09:00')} - ${window.escapeHtml(act.end_time || '11:00')}</span>
          <span class="pill-item">⏳ ${act.duration_minutes || 90} mins</span>
          <span class="pill-item pill-cost">💰 ${costFormatted}</span>
          ${act.is_custom ? '<span class="pill-item" style="background: #F3E8FF; color: #7E22CE;">Custom</span>' : ''}
        </div>
      </div>
    </div>
    ${act.location ? `<div style="font-size: 0.85rem; color: var(--color-teal); font-weight: 600; margin-bottom: 0.5rem;">📍 ${window.escapeHtml(act.location)}</div>` : ''}
    <p class="activity-description">${window.escapeHtml(act.description || '')}</p>
    ${act.transportation_suggestion ? `
      <div class="activity-callout-box">
        <span class="callout-icon">🚇</span>
        <div><strong>Transit:</strong> ${window.escapeHtml(act.transportation_suggestion)}</div>
      </div>
    ` : ''}
    ${act.practical_tips ? `
      <div class="activity-callout-box activity-callout-tip">
        <span class="callout-icon">💡</span>
        <div><strong>Tip:</strong> ${window.escapeHtml(act.practical_tips)}</div>
      </div>
    ` : ''}
    <div class="activity-footer-actions">
      <button class="btn btn-secondary btn-sm" data-action="edit-act" data-id="${act.id}">✏️ Edit</button>
      <button class="btn btn-secondary btn-sm" data-action="delete-act" data-id="${act.id}" style="color: var(--color-rose);">🗑️ Delete</button>
    </div>
  `;

  // Attach event handlers
  card.querySelector("[data-action='edit-act']").addEventListener("click", () => openEditActivityModal(act));
  card.querySelector("[data-action='delete-act']").addEventListener("click", () => handleDeleteActivity(act.id));

  return card;
}

function renderBudgetBreakdown() {
  const container = document.getElementById("budget-breakdown-sidebar");
  if (!container || !currentItinerary) return;

  const totalBudget = currentTrip.total_budget || 0;
  const estimatedCost = currentItinerary.estimated_total_cost || 0;
  const remaining = currentItinerary.remaining_budget || (totalBudget - estimatedCost);
  const costPerPerson = currentItinerary.cost_per_person || (estimatedCost / (currentTrip.num_travelers || 1));
  const currency = currentTrip.currency || "USD";

  const percentUsed = totalBudget > 0 ? Math.min(100, Math.round((estimatedCost / totalBudget) * 100)) : 0;
  const isOverBudget = remaining < 0;

  const cb = currentItinerary.cost_breakdown || {};

  container.innerHTML = `
    <h3 class="budget-card-title">💰 Budget Overview</h3>
    <div class="budget-stat-row">
      <span class="budget-stat-label">Total Allocated:</span>
      <span class="budget-stat-val">${currency} ${Math.round(totalBudget).toLocaleString()}</span>
    </div>
    <div class="budget-stat-row">
      <span class="budget-stat-label">Estimated Total:</span>
      <span class="budget-stat-val">${currency} ${Math.round(estimatedCost).toLocaleString()}</span>
    </div>
    <div class="budget-stat-row">
      <span class="budget-stat-label">Cost per Person:</span>
      <span class="budget-stat-val">${currency} ${Math.round(costPerPerson).toLocaleString()}</span>
    </div>
    <div class="budget-stat-row">
      <span class="budget-stat-label">Remaining:</span>
      <span class="budget-stat-val ${isOverBudget ? 'negative' : 'positive'}">
        ${currency} ${Math.round(remaining).toLocaleString()}
      </span>
    </div>

    <div class="progress-bar-container">
      <div class="progress-bar-fill ${isOverBudget ? 'warning' : ''}" style="width: ${percentUsed}%;"></div>
    </div>
    <div style="font-size: 0.8rem; color: var(--text-muted); text-align: right;">${percentUsed}% of budget used</div>

    <div class="category-breakdown-list">
      <div style="font-size: 0.85rem; font-weight: 700; color: var(--color-primary); margin-bottom: 0.25rem;">Estimated Breakdown</div>
      <div class="cat-item">
        <span class="cat-name"><span class="cat-dot" style="background: #0EA5E9;"></span> Activities</span>
        <span class="cat-amount">${currency} ${Math.round(cb.activities || 0).toLocaleString()}</span>
      </div>
      <div class="cat-item">
        <span class="cat-name"><span class="cat-dot" style="background: #10B981;"></span> Accommodation</span>
        <span class="cat-amount">${currency} ${Math.round(cb.accommodation || 0).toLocaleString()}</span>
      </div>
      <div class="cat-item">
        <span class="cat-name"><span class="cat-dot" style="background: #F59E0B;"></span> Food & Dining</span>
        <span class="cat-amount">${currency} ${Math.round(cb.food || 0).toLocaleString()}</span>
      </div>
      <div class="cat-item">
        <span class="cat-name"><span class="cat-dot" style="background: #8B5CF6;"></span> Transportation</span>
        <span class="cat-amount">${currency} ${Math.round(cb.transportation || 0).toLocaleString()}</span>
      </div>
      <div class="cat-item">
        <span class="cat-name"><span class="cat-dot" style="background: #64748B;"></span> Miscellaneous (5%)</span>
        <span class="cat-amount">${currency} ${Math.round(cb.miscellaneous || 0).toLocaleString()}</span>
      </div>
    </div>
  `;
}

function initItineraryControls(tripId) {
  // Regenerate Day Button
  const regenDayBtn = document.getElementById("regen-day-btn");
  if (regenDayBtn) {
    regenDayBtn.addEventListener("click", () => {
      const modal = document.getElementById("regen-day-modal");
      document.getElementById("regen-day-target-num").textContent = activeDayNumber;
      if (modal) modal.classList.add("show");
    });
  }

  // Regenerate Full Trip Button
  const regenFullBtn = document.getElementById("regen-full-btn");
  if (regenFullBtn) {
    regenFullBtn.addEventListener("click", async () => {
      if (confirm("Regenerate the entire itinerary? This will replace all current daily plans with fresh recommendations.")) {
        regenFullBtn.disabled = true;
        regenFullBtn.innerHTML = `<span class="spinner"></span> Regenerating...`;
        try {
          await window.API.post(`/api/v1/trips/${tripId}/generate`);
          window.showToast("Full itinerary regenerated!", "success");
          await loadTripData(tripId);
        } catch (e) {
          window.showToast(e.message, "error");
        } finally {
          regenFullBtn.disabled = false;
          regenFullBtn.innerHTML = `🔄 Regenerate All`;
        }
      }
    });
  }

  // Add Custom Activity Button
  const addActBtn = document.getElementById("add-activity-btn");
  if (addActBtn) {
    addActBtn.addEventListener("click", () => openAddActivityModal());
  }

  // Print Itinerary
  const printBtn = document.getElementById("print-itinerary-btn");
  if (printBtn) {
    printBtn.addEventListener("click", () => window.print());
  }

  // Copy Summary to Clipboard
  const copyBtn = document.getElementById("copy-summary-btn");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      let text = `TripWise Itinerary: ${currentTrip.title}\n`;
      text += `Destination: ${currentTrip.destination} (${currentTrip.start_date} to ${currentTrip.end_date})\n`;
      text += `Budget: ${currentTrip.currency} ${currentTrip.total_budget}\n\n`;

      currentItinerary.days.forEach(day => {
        text += `--- Day ${day.day_number}: ${day.theme} ---\n`;
        day.activities.forEach(a => {
          text += `• [${a.time_slot || 'Morning'}] ${a.title} (${a.start_time} - ${a.end_time}) - ${a.currency} ${a.estimated_cost}\n  ${a.description}\n`;
        });
        text += "\n";
      });

      navigator.clipboard.writeText(text).then(() => {
        window.showToast("Itinerary summary copied to clipboard!", "success");
      }).catch(() => {
        window.showToast("Could not copy to clipboard.", "error");
      });
    });
  }
}

function initModalListeners(tripId) {
  // Close Modals
  document.querySelectorAll(".modal-close-btn, .modal-cancel-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".modal-backdrop").forEach(m => m.classList.remove("show"));
    });
  });

  // Regenerate Day Submit
  const regenDayForm = document.getElementById("regen-day-form");
  if (regenDayForm) {
    regenDayForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const notes = document.getElementById("regen-day-notes").value.trim();
      const submitBtn = regenDayForm.querySelector("button[type='submit']");
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner"></span> Regenerating...`;

      try {
        await window.API.post(`/api/v1/trips/${tripId}/regenerate-day`, {
          day_number: activeDayNumber,
          prompt_notes: notes
        });
        document.getElementById("regen-day-modal").classList.remove("show");
        window.showToast(`Day ${activeDayNumber} regenerated!`, "success");
        await loadTripData(tripId);
      } catch (err) {
        window.showToast(err.message, "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Regenerate Day";
      }
    });
  }

  // Activity Form (Add / Edit)
  const actForm = document.getElementById("activity-modal-form");
  if (actForm) {
    actForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const actId = document.getElementById("act-edit-id").value;
      const payload = {
        day_number: activeDayNumber,
        title: document.getElementById("act-title").value.trim(),
        time_slot: document.getElementById("act-slot").value,
        start_time: document.getElementById("act-start-time").value,
        end_time: document.getElementById("act-end-time").value,
        location: document.getElementById("act-location").value.trim(),
        duration_minutes: parseInt(document.getElementById("act-duration").value, 10) || 90,
        estimated_cost: parseFloat(document.getElementById("act-cost").value) || 0,
        currency: currentTrip.currency || "USD",
        description: document.getElementById("act-description").value.trim(),
        transportation_suggestion: document.getElementById("act-transit").value.trim(),
        practical_tips: document.getElementById("act-tips").value.trim()
      };

      const submitBtn = actForm.querySelector("button[type='submit']");
      submitBtn.disabled = true;

      try {
        if (actId) {
          // Update
          await window.API.put(`/api/v1/trips/${tripId}/activities/${actId}`, payload);
          window.showToast("Activity updated!", "success");
        } else {
          // Add
          await window.API.post(`/api/v1/trips/${tripId}/activities`, payload);
          window.showToast("Custom activity added!", "success");
        }
        document.getElementById("activity-modal").classList.remove("show");
        await loadTripData(tripId);
      } catch (err) {
        window.showToast(err.message, "error");
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
}

function openAddActivityModal() {
  document.getElementById("activity-modal-title").textContent = `Add Activity to Day ${activeDayNumber}`;
  document.getElementById("act-edit-id").value = "";
  document.getElementById("activity-modal-form").reset();
  document.getElementById("act-duration").value = "90";
  document.getElementById("act-cost").value = "0";
  document.getElementById("activity-modal").classList.add("show");
}

function openEditActivityModal(act) {
  document.getElementById("activity-modal-title").textContent = "Edit Activity";
  document.getElementById("act-edit-id").value = act.id;
  document.getElementById("act-title").value = act.title || "";
  document.getElementById("act-slot").value = act.time_slot || "Morning";
  document.getElementById("act-start_time").value = act.start_time || "09:00";
  document.getElementById("act-end_time").value = act.end_time || "11:00";
  document.getElementById("act-location").value = act.location || "";
  document.getElementById("act-duration").value = act.duration_minutes || 90;
  document.getElementById("act-cost").value = act.estimated_cost || 0;
  document.getElementById("act-description").value = act.description || "";
  document.getElementById("act-transit").value = act.transportation_suggestion || "";
  document.getElementById("act-tips").value = act.practical_tips || "";
  document.getElementById("activity-modal").classList.add("show");
}

async function handleDeleteActivity(actId) {
  if (confirm("Delete this activity? Budget estimates will be updated automatically.")) {
    try {
      await window.API.delete(`/api/v1/trips/${currentTrip.id}/activities/${actId}`);
      window.showToast("Activity removed.", "info");
      await loadTripData(currentTrip.id);
    } catch (e) {
      window.showToast(e.message, "error");
    }
  }
}
