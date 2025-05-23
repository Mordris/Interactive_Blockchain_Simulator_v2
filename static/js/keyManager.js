// static/js/keyManager.js
import { showNotification } from "./utils.js";
import { generateKeysAPI, requestWelcomeBonusAPI } from "./apiClient.js";
import { updateBalanceUI } from "./uiUpdater.js";

export let userKeys = {
  private_key_pem: null,
  public_key_pem: null,
};

export function getPublicKey() {
  return userKeys.public_key_pem;
}
export function getPrivateKey() {
  return userKeys.private_key_pem;
}

// Updates the UI elements related to the active browser user's keys
function setKeyUIElements(fullKey) {
  // fullKey can be null
  const pkDisplayElement = document.getElementById("user-public-key-display");
  const pkFullInputElement_forCopy = document.getElementById(
    "user-public-key-full-for-copy"
  );
  const senderPkTextareaElement = document.getElementById("sender-public-key");
  const minerPkTextareaElement = document.getElementById(
    "miner-address-public-key"
  );

  const keyToDisplay = fullKey || ""; // Use empty string if fullKey is null

  if (pkDisplayElement) {
    pkDisplayElement.value = keyToDisplay;
    if (!fullKey) {
      pkDisplayElement.placeholder = "Generate keys to see your public key...";
    }
  }
  if (pkFullInputElement_forCopy) {
    pkFullInputElement_forCopy.value = keyToDisplay;
  }
  if (senderPkTextareaElement) {
    senderPkTextareaElement.value = keyToDisplay;
  }
  if (minerPkTextareaElement) {
    // This field is now editable, but we pre-fill it with the active user's key
    minerPkTextareaElement.value = keyToDisplay;
    if (!fullKey) {
      minerPkTextareaElement.placeholder =
        "Generate your keys to pre-fill or paste a miner's public key";
    }
  }
}

export function loadUserKeys() {
  const storedKeys = localStorage.getItem("blockchainUserKeys");
  const balanceElement = document.getElementById("user-balance");

  if (storedKeys) {
    try {
      userKeys = JSON.parse(storedKeys);
      if (userKeys && userKeys.public_key_pem && userKeys.private_key_pem) {
        setKeyUIElements(userKeys.public_key_pem);
        updateBalanceUI();
      } else {
        userKeys = { private_key_pem: null, public_key_pem: null };
        localStorage.removeItem("blockchainUserKeys");
        setKeyUIElements(null);
        if (balanceElement) balanceElement.textContent = "N/A";
        showNotification(
          "Stored key data was invalid. Please generate new keys.",
          true
        );
      }
    } catch (e) {
      console.error("Error parsing stored keys:", e);
      localStorage.removeItem("blockchainUserKeys");
      userKeys = { private_key_pem: null, public_key_pem: null };
      setKeyUIElements(null);
      if (balanceElement) balanceElement.textContent = "N/A";
      showNotification(
        "Could not load stored keys. Please generate new ones.",
        true
      );
    }
  } else {
    setKeyUIElements(null); // Ensure UI is cleared if no keys are stored
    if (balanceElement) balanceElement.textContent = "N/A";
    // Optionally, don't show a notification if no keys are found, let user generate them.
    // showNotification("No keys found in local storage. Please generate a key pair.", false);
  }
}

export async function generateAndStoreUserKeys() {
  const result = await generateKeysAPI();
  if (result.success && result.private_key_pem && result.public_key_pem) {
    userKeys = {
      private_key_pem: result.private_key_pem,
      public_key_pem: result.public_key_pem,
    };
    localStorage.setItem("blockchainUserKeys", JSON.stringify(userKeys));
    showNotification("New key pair generated and stored locally!");
    setKeyUIElements(userKeys.public_key_pem); // Update all relevant UI fields

    const bonusResult = await requestWelcomeBonusAPI(userKeys.public_key_pem);
    if (bonusResult.success) {
      showNotification(
        bonusResult.message || "Welcome bonus processing initiated!"
      );
    }
    // Balance update will be triggered by socket event after bonus mining
  } else {
    showNotification(
      "Failed to generate keys: " + (result.error || "Unknown error from API"),
      true
    );
  }
}

export async function copyPublicKeyToClipboard() {
  const fullKeyToCopy = userKeys.public_key_pem;

  if (!fullKeyToCopy) {
    showNotification("No active public key available to copy.", true);
    return;
  }

  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(fullKeyToCopy);
      showNotification("Active Public key copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy using navigator.clipboard:", err);
      tryToUseExecCommandFallback(fullKeyToCopy);
    }
  } else {
    tryToUseExecCommandFallback(fullKeyToCopy);
  }
}

function tryToUseExecCommandFallback(textToCopy) {
  const hiddenInputForCopy = document.getElementById(
    "user-public-key-full-for-copy"
  );
  if (!hiddenInputForCopy) {
    showNotification("Copy feature setup error. Please copy manually.", true);
    return;
  }
  hiddenInputForCopy.value = textToCopy;

  hiddenInputForCopy.style.display = "block";
  hiddenInputForCopy.style.position = "fixed";
  hiddenInputForCopy.style.left = "-9999px";

  hiddenInputForCopy.select();
  hiddenInputForCopy.setSelectionRange(0, textToCopy.length);

  let successful = false;
  try {
    successful = document.execCommand("copy");
    if (successful) {
      showNotification("Public key copied! (fallback method)");
    } else {
      throw new Error('document.execCommand("copy") returned false.');
    }
  } catch (err) {
    showNotification(
      "Failed to copy public key using fallback. Please copy manually.",
      true
    );
    console.error("execCommand copy failed:", err);
  } finally {
    hiddenInputForCopy.style.display = "none";
    hiddenInputForCopy.style.position = "absolute";
    if (window.getSelection && window.getSelection().removeAllRanges) {
      window.getSelection().removeAllRanges();
    } else if (document.selection && document.selection.empty) {
      document.selection.empty();
    }
  }
}
