// static/js/uiUpdater.js
import {
  animateNumberChange,
  formatTimestamp,
  formatHash,
  showNotification,
} from "./utils.js";
import { getBalanceAPI, getUserDirectoryAPI } from "./apiClient.js";
import { getPublicKey } from "./keyManager.js"; // To get the active user's public key

// Updates the balance display for the currently active browser user
export async function updateBalanceUI() {
  const activeUserPublicKeyPem = getPublicKey();
  const balanceElement = document.getElementById("user-balance");

  if (!balanceElement) return;

  if (!activeUserPublicKeyPem) {
    balanceElement.textContent = "N/A (Generate Keys)";
    return;
  }

  const encodedPublicKey = encodeURIComponent(activeUserPublicKeyPem);
  const result = await getBalanceAPI(encodedPublicKey);

  if (result.success) {
    balanceElement.textContent = parseFloat(result.balance).toFixed(4);
  } else {
    balanceElement.textContent = "Error";
    // Error notification is handled by apiClient's fetchAPI if it was an API error
    // If it's a logical error from getBalance (e.g. no blockchain), showNotification might be called there
  }
}

// Updates the main status dashboard
export function updateDashboardUI(status) {
  if (!status) return;
  animateNumberChange("block-count", String(status.blocks));
  animateNumberChange("pending-tx-count", String(status.pending_transactions));
  animateNumberChange("difficulty-status", String(status.difficulty));
  animateNumberChange(
    "mining-reward-status",
    parseFloat(status.mining_reward).toFixed(1)
  );
}

// Renders the blockchain visualizer
export function updateBlockchainDisplayUI(blocks) {
  const container = document.getElementById("blockchain-display");
  if (!container) return;
  container.innerHTML = "";

  if (!blocks || blocks.length === 0) {
    container.innerHTML =
      '<p class="text-center text-muted fst-italic my-3">Blockchain is empty.</p>';
    return;
  }

  [...blocks].reverse().forEach((block) => {
    // Show newest blocks at the top
    const blockElement = document.createElement("div");
    blockElement.className = "block card mb-3 shadow-sm";
    const transactionsHtml =
      block.transactions.length > 0
        ? block.transactions
            .map((tx) => {
              const senderDisplay =
                tx.sender_public_key === "network" ||
                tx.sender_public_key === "welcome_faucet" ||
                tx.sender_public_key === "GENESIS_ALLOCATION"
                  ? `<strong class="text-primary">${tx.sender_public_key.toUpperCase()}</strong>`
                  : `<span title="Sender PK: ${
                      tx.sender_public_key
                    }">${formatHash(tx.sender_public_key, 6)}</span>`;

              const recipientDisplay = `<span title="Recipient PK: ${
                tx.recipient_public_key
              }">${formatHash(tx.recipient_public_key, 6)}</span>`;

              const amountClass =
                tx.sender_public_key === "network" ||
                tx.sender_public_key === "welcome_faucet" ||
                tx.sender_public_key === "GENESIS_ALLOCATION"
                  ? "text-success" // Green for incoming system funds
                  : "text-danger"; // Red for outgoing user funds (from perspective of chain, not specific user)

              const amountPrefix =
                tx.sender_public_key === "network" ||
                tx.sender_public_key === "welcome_faucet" ||
                tx.sender_public_key === "GENESIS_ALLOCATION"
                  ? "+"
                  : "-"; // This might be confusing; tx list doesn't know "my" perspective. Let's keep it simple.

              return `
              <div class="transaction-item small p-1 mb-1 border rounded d-flex justify-content-between align-items-center">
                  <span class="text-truncate" style="max-width: 70%;">
                     <i class="bi bi-arrow-right-circle me-1"></i>
                     From: ${senderDisplay} → To: ${recipientDisplay}
                  </span>
                  <span class="fw-bold ms-2 ${amountClass}">
                     ${parseFloat(tx.amount).toFixed(2)}
                  </span>
              </div>`;
            })
            .join("")
        : '<p class="fst-italic text-muted my-1">No transactions in this block.</p>';

    blockElement.innerHTML = `
      <div class="card-header block-header d-flex justify-content-between align-items-center">
          <span class="block-index fw-bold text-primary">Block #${
            block.index
          }</span>
          <span class="block-hash text-muted small" title="Full Hash: ${
            block.hash
          }">${formatHash(block.hash, 8)}</span>
      </div>
      <div class="card-body block-details py-2 px-3">
          <p class="card-text small mb-1"><strong>Prev. Hash:</strong> <span class="text-muted" title="Full Previous Hash: ${
            block.previous_hash
          }">${formatHash(block.previous_hash, 8)}</span></p>
          <p class="card-text small mb-1"><strong>Timestamp:</strong> <span class="text-muted">${formatTimestamp(
            block.timestamp
          )}</span></p>
          <p class="card-text small mb-1"><strong>Nonce:</strong> <span class="text-muted">${
            block.nonce
          }</span></p>
      </div>
      <div class="card-footer transactions-list small py-2 px-3">
          <h6 class="small mb-1 fw-bold">Transactions (${
            block.transactions.length
          }):</h6>
          ${transactionsHtml}
      </div>
    `;
    container.appendChild(blockElement);
  });
}

// Populates the User Directory UI
export function populateUserDirectoryUI(users) {
  const directoryContainer = document.getElementById("user-directory-display");
  const directoryCountElement = document.getElementById("user-directory-count");

  if (!directoryContainer) return;
  directoryContainer.innerHTML = "";

  if (directoryCountElement) {
    directoryCountElement.textContent = `${users ? users.length : 0} Users`;
  }

  if (!users || users.length === 0) {
    directoryContainer.innerHTML =
      '<p class="text-center text-muted fst-italic my-2">No predefined users found.</p>';
    return;
  }

  users.forEach((user) => {
    const entryDiv = document.createElement("div");
    // Use flex utilities for layout within each entry
    entryDiv.className =
      "user-directory-entry d-flex justify-content-between align-items-center py-1";

    const userInfoDiv = document.createElement("div"); // For name and short PK
    userInfoDiv.className = "me-2"; // Margin to separate from balance/copy button

    const nameSpan = document.createElement("span");
    nameSpan.textContent = user.name;
    nameSpan.className = "user-name-clickable d-block";
    nameSpan.title = `Click to set ${user.name} as Miner Reward Address`;
    nameSpan.addEventListener("click", () => {
      const minerAddressField = document.getElementById(
        "miner-address-public-key"
      );
      if (minerAddressField) {
        minerAddressField.value = user.public_key_pem;
        minerAddressField.scrollTop = 0;
        minerAddressField.focus();
        showNotification(
          `${user.name}'s PK populated in Miner Reward Address field!`
        );
      }
    });

    const keySpanDisplay = document.createElement("span"); // For displaying shortened key
    keySpanDisplay.className = "user-pubkey-short";
    keySpanDisplay.textContent = formatHash(user.public_key_pem, 10);
    keySpanDisplay.title = `Full PK: ${user.public_key_pem}\nClick to populate Recipient field.`;
    keySpanDisplay.addEventListener("click", (e) => {
      e.stopPropagation();
      const recipientField = document.getElementById("recipient-public-key");
      if (recipientField) {
        recipientField.value = user.public_key_pem;
        recipientField.scrollTop = 0;
        recipientField.focus();
        showNotification(`${user.name}'s PK populated in Recipient field!`);
      }
    });

    userInfoDiv.appendChild(nameSpan);
    userInfoDiv.appendChild(keySpanDisplay);

    const actionsDiv = document.createElement("div"); // For balance and copy button
    actionsDiv.className = "d-flex align-items-center";

    const balanceSpan = document.createElement("span");
    balanceSpan.className = "directory-balance badge bg-info text-dark me-2"; // Added margin
    balanceSpan.textContent =
      typeof user.balance === "number"
        ? `${parseFloat(user.balance).toFixed(2)} Coins`
        : user.balance;

    // --- NEW COPY BUTTON ---
    const copyBtn = document.createElement("button");
    copyBtn.className = "btn btn-sm btn-outline-secondary p-1"; // Small padding
    copyBtn.innerHTML = '<i class="bi bi-clipboard"></i>';
    copyBtn.title = `Copy ${user.name}'s Public Key`;
    copyBtn.style.fontSize = "0.7rem"; // Make icon/button smaller

    copyBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // Prevent other clicks if nested
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(user.public_key_pem)
          .then(() =>
            showNotification(`Copied ${user.name}'s Public Key to clipboard.`)
          )
          .catch((err) => {
            console.error("Failed to copy directory key to clipboard:", err);
            showNotification(`Could not auto-copy ${user.name}'s PK.`, true);
          });
      } else {
        showNotification(
          `Browser does not support modern clipboard API. Cannot auto-copy.`,
          true
        );
      }
    });
    // --- END NEW COPY BUTTON ---

    actionsDiv.appendChild(balanceSpan);
    actionsDiv.appendChild(copyBtn); // Add copy button to actions

    entryDiv.appendChild(userInfoDiv);
    entryDiv.appendChild(actionsDiv); // Add actions div (balance + copy)
    directoryContainer.appendChild(entryDiv);
  });
}

// Main function called by socketHandler when blockchain data is received
export async function handleBlockchainUpdateFromSocket(data) {
  if (!data) return;

  if (data.status) {
    updateDashboardUI(data.status);
  }
  if (data.blocks) {
    updateBlockchainDisplayUI(data.blocks);
  }
  updateBalanceUI(); // Update active browser user's balance

  // Refresh user directory to update all listed users' balances
  const usersDirectoryResult = await getUserDirectoryAPI();
  if (usersDirectoryResult.success === false) {
    // Check explicit failure from API client
    // Error already shown by apiClient if it was a fetch issue
    // populateUserDirectoryUI([]); // Optionally clear or show error in directory
    console.error(
      "Failed to refresh user directory:",
      usersDirectoryResult.error
    );
  } else if (Array.isArray(usersDirectoryResult)) {
    // Success, result is the array
    populateUserDirectoryUI(usersDirectoryResult);
  }
}
