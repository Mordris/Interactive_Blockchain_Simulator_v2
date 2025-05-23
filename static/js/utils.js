// static/js/utils.js

// Toast notifications
const toastElement = document.getElementById("toast");
const toast = toastElement ? new bootstrap.Toast(toastElement) : null;

export function showNotification(message, isError = false) {
  if (!toast || !toastElement) {
    console.warn("Toast element not found, notification not shown:", message);
    // Fallback to alert if toast is not available for some reason
    alert((isError ? "Error: " : "Notification: ") + message);
    return;
  }
  const toastBody = toastElement.querySelector(".toast-body");
  const toastHeader = toastElement.querySelector(".toast-header");

  if (toastBody) toastBody.textContent = message;
  if (toastHeader) {
    // Clear previous color classes
    toastHeader.classList.remove("bg-danger", "text-white", "bg-success");
    // Add new classes
    if (isError) {
      toastHeader.classList.add("bg-danger", "text-white");
    } else {
      toastHeader.classList.add("bg-success", "text-white");
    }
  }
  toast.show();
}

// Helper: Animate number changes
let lastKnownStatusValues = {};
export function animateNumberChange(elementId, newValueText) {
  const element = document.getElementById(elementId);
  if (!element) {
    // console.warn(`Element with ID '${elementId}' not found for animation.`);
    return;
  }

  const targetValue = parseFloat(newValueText);
  const currentValueText = element.textContent;
  // Try to parse current text, default to 0 if not a number or empty
  const currentNumericValue = parseFloat(currentValueText);
  const lastKnown = lastKnownStatusValues[elementId];

  // If current display already matches newValueText, and last known value also matches target, skip
  if (currentValueText === String(newValueText) && lastKnown === targetValue) {
    return;
  }

  element.classList.add("status-update");
  element.textContent = newValueText;
  lastKnownStatusValues[elementId] = targetValue;

  setTimeout(() => {
    element.classList.remove("status-update");
  }, 1000); // Duration of the CSS animation
}

// Helper: Format timestamp
export function formatTimestamp(timestamp) {
  if (timestamp === null || timestamp === undefined || isNaN(timestamp))
    return "N/A";
  return new Date(timestamp * 1000).toLocaleString();
}

// Helper: Format hash for display
export function formatHash(hash, length = 10) {
  if (!hash || typeof hash !== "string") return "Invalid Hash";
  if (hash.length < length * 2 + 3) return hash; // If too short for meaningful truncation
  return (
    hash.substring(0, length) + "..." + hash.substring(hash.length - length)
  );
}
