/**
 * TripWise AI — Multi-Step Trip Planner Wizard
 */

let currentStep = 1;
const totalSteps = 5;

const tripFormData = {
  destination: "",
  origin: "",
  start_date: "",
  end_date: "",
  num_travelers: 1,
  total_budget: 1500,
  currency: "USD",
  travel_style: "standard",
  travel_pace: "balanced",
  interests: ["sightseeing", "food"],
  accommodation_preference: "hotel",
  transportation_preference: "public_transit",
  dietary_restrictions: [],
  additional_notes: ""
};

document.addEventListener("DOMContentLoaded", () => {
  initFormControls();
  initStepNavigation();
  updateStepView();
});

function initFormControls() {
  // Set default dates: tomorrow to +4 days
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const end = new Date(tomorrow);
  end.setDate(end.getDate() + 3);

  const startInput = document.getElementById("start_date");
  const endInput = document.getElementById("end_date");

  if (startInput && endInput) {
    const toISO = (d) => d.toISOString().split("T")[0];
    startInput.min = toISO(today);
    startInput.value = toISO(tomorrow);
    endInput.min = toISO(tomorrow);
    endInput.value = toISO(end);

    startInput.addEventListener("change", () => {
      endInput.min = startInput.value;
      if (endInput.value < startInput.value) {
        endInput.value = startInput.value;
      }
    });
  }

  // Option Pills for Travel Style
  document.querySelectorAll("[data-style-val]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-style-val]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      tripFormData.travel_style = btn.dataset.styleVal;
    });
  });

  // Option Pills for Travel Pace
  document.querySelectorAll("[data-pace-val]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-pace-val]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      tripFormData.travel_pace = btn.dataset.paceVal;
    });
  });

  // Interest Tag Checkboxes
  document.querySelectorAll("[data-interest-val]").forEach(tag => {
    tag.addEventListener("click", () => {
      tag.classList.toggle("active");
      const val = tag.dataset.interestVal;
      if (tag.classList.contains("active")) {
        if (!tripFormData.interests.includes(val)) tripFormData.interests.push(val);
      } else {
        tripFormData.interests = tripFormData.interests.filter(i => i !== val);
      }
    });
  });
}

function initStepNavigation() {
  const nextBtn = document.getElementById("wizard-next-btn");
  const prevBtn = document.getElementById("wizard-prev-btn");
  const submitBtn = document.getElementById("wizard-submit-btn");

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      if (validateCurrentStep()) {
        currentStep++;
        updateStepView();
      }
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (currentStep > 1) {
        currentStep--;
        updateStepView();
      }
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", handleTripGeneration);
  }
}

function validateCurrentStep() {
  if (currentStep === 1) {
    const dest = document.getElementById("destination").value.trim();
    const start = document.getElementById("start_date").value;
    const end = document.getElementById("end_date").value;

    if (!dest) {
      window.showToast("Please enter a destination city or country.", "error");
      return false;
    }
    if (!start || !end) {
      window.showToast("Please select your travel dates.", "error");
      return false;
    }
    if (end < start) {
      window.showToast("Return date cannot be before departure date.", "error");
      return false;
    }

    tripFormData.destination = dest;
    tripFormData.origin = document.getElementById("origin").value.trim();
    tripFormData.start_date = start;
    tripFormData.end_date = end;
    return true;
  }

  if (currentStep === 2) {
    const travelers = parseInt(document.getElementById("num_travelers").value, 10);
    const budget = parseFloat(document.getElementById("total_budget").value);
    const currency = document.getElementById("currency").value;

    if (isNaN(travelers) || travelers < 1) {
      window.showToast("Number of travelers must be at least 1.", "error");
      return false;
    }
    if (isNaN(budget) || budget < 0) {
      window.showToast("Please enter a valid budget amount.", "error");
      return false;
    }

    tripFormData.num_travelers = travelers;
    tripFormData.total_budget = budget;
    tripFormData.currency = currency;
    return true;
  }

  if (currentStep === 3) {
    if (tripFormData.interests.length === 0) {
      window.showToast("Please select at least one travel interest.", "error");
      return false;
    }
    return true;
  }

  if (currentStep === 4) {
    tripFormData.accommodation_preference = document.getElementById("accommodation_preference").value;
    tripFormData.transportation_preference = document.getElementById("transportation_preference").value;
    tripFormData.additional_notes = document.getElementById("additional_notes").value.trim();

    // Dietary checkboxes
    const dietary = [];
    document.querySelectorAll("input[name='dietary']:checked").forEach(cb => {
      dietary.push(cb.value);
    });
    tripFormData.dietary_restrictions = dietary;
    return true;
  }

  return true;
}

function updateStepView() {
  // Hide all step sections
  for (let i = 1; i <= totalSteps; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    if (stepEl) stepEl.style.display = (i === currentStep) ? "block" : "none";

    const indicator = document.getElementById(`indicator-step-${i}`);
    if (indicator) {
      indicator.classList.remove("active", "completed");
      if (i === currentStep) indicator.classList.add("active");
      else if (i < currentStep) indicator.classList.add("completed");
    }
  }

  const prevBtn = document.getElementById("wizard-prev-btn");
  const nextBtn = document.getElementById("wizard-next-btn");
  const submitBtn = document.getElementById("wizard-submit-btn");

  if (prevBtn) prevBtn.style.display = (currentStep === 1) ? "none" : "inline-flex";
  if (nextBtn) nextBtn.style.display = (currentStep === totalSteps) ? "none" : "inline-flex";
  if (submitBtn) submitBtn.style.display = (currentStep === totalSteps) ? "inline-flex" : "none";

  if (currentStep === totalSteps) {
    populateReviewStep();
  }
}

function populateReviewStep() {
  const container = document.getElementById("review-summary-card");
  if (!container) return;

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem;">
      <div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Destination</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--color-primary);">📍 ${window.escapeHtml(tripFormData.destination)}</div>
      </div>
      <div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Travel Dates</div>
        <div style="font-size: 1rem; font-weight: 600;">📅 ${window.escapeHtml(tripFormData.start_date)} to ${window.escapeHtml(tripFormData.end_date)}</div>
      </div>
      <div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Party & Budget</div>
        <div style="font-size: 1rem; font-weight: 600;">👥 ${tripFormData.num_travelers} • 💰 ${tripFormData.currency} ${tripFormData.total_budget.toLocaleString()}</div>
      </div>
      <div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Style & Pace</div>
        <div style="font-size: 1rem; font-weight: 600; text-transform: capitalize;">✨ ${tripFormData.travel_style} • ⚡ ${tripFormData.travel_pace}</div>
      </div>
    </div>
    <div style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem;">
      <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem;">Interests</div>
      <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
        ${tripFormData.interests.map(i => `<span class="badge badge-planning">${window.escapeHtml(i)}</span>`).join('')}
      </div>
    </div>
  `;
}

async function handleTripGeneration() {
  const submitBtn = document.getElementById("wizard-submit-btn");
  const loadingOverlay = document.getElementById("generation-loading-overlay");
  const statusMsg = document.getElementById("generation-status-text");

  submitBtn.disabled = true;
  if (loadingOverlay) loadingOverlay.style.display = "flex";

  const progressMessages = [
    "Analyzing your destination and travel dates...",
    "Selecting top-rated landmarks and hidden gems...",
    "Optimizing geographic routes to save transit time...",
    "Structuring daily schedule and calculating budgets..."
  ];

  let msgIdx = 0;
  const interval = setInterval(() => {
    msgIdx = (msgIdx + 1) % progressMessages.length;
    if (statusMsg) statusMsg.textContent = progressMessages[msgIdx];
  }, 1200);

  try {
    const createdTrip = await window.API.post("/api/v1/trips", tripFormData);
    clearInterval(interval);
    window.showToast("Your AI itinerary is ready!", "success");
    setTimeout(() => {
      window.location.href = `itinerary.html?id=${createdTrip.id}`;
    }, 600);
  } catch (err) {
    clearInterval(interval);
    if (loadingOverlay) loadingOverlay.style.display = "none";
    submitBtn.disabled = false;
    window.showToast(err.message || "Failed to generate itinerary. Please try again.", "error");
  }
}
