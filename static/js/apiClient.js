// static/js/apiClient.js
import { showNotification } from "./utils.js";

const API_BASE_URL = ""; // Assuming API is on the same origin

async function fetchAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    if (!response.ok) {
      let errorData = { error: `HTTP error! status: ${response.status}` }; // Default error
      try {
        // Try to get more specific error from JSON response body
        const jsonError = await response.json();
        if (jsonError && jsonError.error) {
          errorData.error = jsonError.error;
        }
      } catch (e) {
        // If response body is not JSON or empty, use the default HTTP error
        console.warn(
          "Could not parse JSON error from response for",
          endpoint,
          e
        );
      }
      throw new Error(errorData.error);
    }
    // Handle 204 No Content specifically
    if (response.status === 204) {
      return { success: true, data: null }; // Or just undefined, depending on how you want to handle it
    }
    return await response.json(); // Assumes all other successful responses are JSON
  } catch (error) {
    console.error(
      `API Error (${options.method || "GET"} ${endpoint}):`,
      error.message
    );
    // showNotification is called by the calling function based on the returned error object
    // This allows more contextual error messages if needed.
    // showNotification(`API Error: ${error.message}`, true);
    return {
      success: false,
      error: error.message,
      status: options.status || 500,
    }; // Return a consistent error object
  }
}

export async function generateKeysAPI() {
  return fetchAPI("/api/keys/generate", { method: "POST" });
}

export async function getUserDirectoryAPI() {
  return fetchAPI("/api/users/directory"); // GET request by default
}

export async function createBlockchainAPI(difficulty, miningReward) {
  const result = await fetchAPI("/api/blockchain/create", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      difficulty: parseInt(difficulty),
      mining_reward: parseFloat(miningReward),
    }),
  });
  if (!result.success)
    showNotification(result.error || "Failed to create blockchain.", true);
  return result;
}

export async function getBalanceAPI(encodedPublicKey) {
  const result = await fetchAPI(
    `/api/blockchain/balance?key=${encodedPublicKey}`
  );
  // Don't show notification here, let UI decide how to display error or N/A
  // if (!result.success) showNotification("Error fetching balance: " + result.error, true);
  return result;
}

// Insecure signing - ONLY FOR DEMO - private key should NOT be sent to server
export async function signDataInsecureAPI(privateKeyPem, dataToSign) {
  const result = await fetchAPI("/api/utils/sign-data-for-client", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      private_key_pem: privateKeyPem,
      data_to_sign: dataToSign,
    }),
  });
  if (!result.success)
    showNotification(
      "Error signing data: " + (result.error || "Unknown"),
      true
    );
  return result;
}

export async function addTransactionAPI(payload) {
  const result = await fetchAPI("/api/blockchain/add-transaction", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!result.success)
    showNotification(
      "Error adding transaction: " + (result.error || "Unknown"),
      true
    );
  return result;
}

export async function mineBlockAPI(minerAddressPublicKey) {
  const result = await fetchAPI("/api/blockchain/mine", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ miner_address_public_key: minerAddressPublicKey }),
  });
  // Success message is usually handled by the calling function based on result.message
  if (!result.success)
    showNotification(
      "Error mining block: " + (result.error || "Unknown"),
      true
    );
  return result;
}

export async function validateChainAPI() {
  const result = await fetchAPI("/api/blockchain/validate");
  // Notification handled by caller based on result.valid
  return result;
}

export async function saveBlockchainAPI() {
  const result = await fetchAPI("/api/blockchain/save");
  if (!result.success)
    showNotification(
      "Error saving blockchain: " + (result.error || "Unknown"),
      true
    );
  return result;
}

export async function requestWelcomeBonusAPI(recipientPublicKey) {
  const result = await fetchAPI("/api/faucet/request-welcome-bonus", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recipient_public_key: recipientPublicKey }),
  });
  if (!result.success)
    showNotification(
      "Error requesting welcome bonus: " + (result.error || "Unknown"),
      true
    );
  return result;
}
