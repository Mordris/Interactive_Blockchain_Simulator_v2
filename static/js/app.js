// static/js/app.js
import { showNotification } from "./utils.js";
import {
  createBlockchainAPI,
  addTransactionAPI,
  signDataInsecureAPI,
  mineBlockAPI,
  validateChainAPI,
  saveBlockchainAPI,
} from "./apiClient.js";
import {
  loadUserKeys,
  generateAndStoreUserKeys,
  copyPublicKeyToClipboard,
  getPublicKey,
  getPrivateKey,
} from "./keyManager.js";
import { initializeSocket } from "./socketHandler.js";

// --- DOM Element Cache ---
const domCache = {
  get: (id) => document.getElementById(id),
  query: (selector) => document.querySelector(selector),
};

const elements = {
  // Modals
  createBlockchainModalEl: domCache.get("createBlockchainModal"),
  miningModalEl: domCache.get("miningModal"),
  infoModalEl: domCache.get("infoModal"),

  // Buttons
  createBlockchainBtn: domCache.get("create-blockchain-btn"),
  generateKeysBtn: domCache.get("generate-keys-btn"),
  copyPkBtn: domCache.get("copy-pk-btn"),
  validateChainBtn: domCache.get("validate-chain-btn"),
  saveChainBtn: domCache.get("save-chain-btn"),
  // gotItInfoModalBtn: domCache.get("got-it-info-modal-btn"), // Not strictly needed if we use hidden.bs.modal

  // Forms
  transactionForm: domCache.get("transaction-form"),
  miningForm: domCache.get("mining-form"),

  // Inputs & Textareas
  difficultyInput: domCache.get("difficulty"),
  miningRewardInput: domCache.get("mining-reward"),
  recipientPublicKeyInput: domCache.get("recipient-public-key"),
  amountInput: domCache.get("amount"),
  senderPublicKeyTextarea: domCache.get("sender-public-key"),
  minerAddressPublicKeyTextarea: domCache.get("miner-address-public-key"),

  // Mining Modal UI
  miningAttemptsEl: domCache.get("mining-attempts"),
  miningTimeEl: domCache.get("mining-time"),
  miningProgressEl: domCache.get("mining-progress"),
  miningHashValueEl: domCache.query("#mining-hash-display .hash-value"),
};

let miningAnimationInterval = null;

// --- Form and Button Event Listeners ---

if (elements.createBlockchainBtn) {
  elements.createBlockchainBtn.addEventListener("click", async () => {
    if (!elements.difficultyInput || !elements.miningRewardInput) {
      showNotification(
        "Internal error: Difficulty or reward input not found.",
        true
      );
      return;
    }

    elements.createBlockchainBtn.disabled = true;
    elements.createBlockchainBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';

    const result = await createBlockchainAPI(
      elements.difficultyInput.value,
      elements.miningRewardInput.value
    );

    // Inside the createBlockchainBtn listener in app.js, on success:
    if (result.success) {
      showNotification(result.message || "Blockchain created successfully!");
      const modalEl = document.getElementById("createBlockchainModal"); // Direct DOM get
      if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl); // Try getInstance first
        if (modal) {
          console.log(
            "Hiding modal via getInstance for #createBlockchainModal"
          );
          modal.hide();
        } else {
          // If getInstance is null, Bootstrap might not have initialized it via data attributes yet
          // or it was disposed. This path is less ideal.
          console.warn(
            "bootstrap.Modal.getInstance for #createBlockchainModal returned null. Modal might not hide or might error if re-shown via JS."
          );
        }
      }
    } else {
        // Also hide modal and re-enable button on failure
        const modalEl = document.getElementById("createBlockchainModal");
         if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) {
              console.log(
                "Hiding modal via getInstance for #createBlockchainModal on failure"
              );
              modal.hide();
            }
         }
    }

    // Always re-enable button after API call completes
    elements.createBlockchainBtn.disabled = false;
    elements.createBlockchainBtn.innerHTML = '<i class="bi bi-plus-circle me-1"></i> Create Blockchain'; // Restore original text

  });
}

if (elements.transactionForm) {
  elements.transactionForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const addTxButton = e.target.querySelector('button[type="submit"]');
    const originalButtonText = addTxButton.innerHTML;

    const privateKey = getPrivateKey();
    const senderPublicKey = getPublicKey();

    if (!privateKey || !senderPublicKey) {
      showNotification(
        "Please generate/load your keys first to send a transaction.",
        true
      );
      return;
    }
    if (!elements.recipientPublicKeyInput || !elements.amountInput) return;

    const recipientPublicKey = elements.recipientPublicKeyInput.value;
    const amount = parseFloat(elements.amountInput.value);

    if (!recipientPublicKey.trim() || !(amount > 0)) {
      showNotification(
        "Valid Recipient Public Key (non-empty) and a positive Amount are required.",
        true
      );
      return;
    }

    addTxButton.disabled = true;
    addTxButton.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';

    const dataToSign = `${senderPublicKey}${recipientPublicKey}${amount.toFixed(
      8
    )}`;

    const signResult = await signDataInsecureAPI(privateKey, dataToSign);
    if (!signResult.success || !signResult.signature) {
      addTxButton.disabled = false;
      addTxButton.innerHTML = originalButtonText;
      return; // Notification handled by apiClient
    }
    const signature = signResult.signature;

    const addTxResult = await addTransactionAPI({
      sender_public_key: senderPublicKey,
      recipient_public_key: recipientPublicKey,
      amount,
      signature,
    });

    if (addTxResult.success) {
      showNotification(
        addTxResult.message || "Transaction added to pending pool!"
      );
      e.target.reset(); // Reset form
      if (elements.senderPublicKeyTextarea)
        elements.senderPublicKeyTextarea.value = senderPublicKey;
      if (
        elements.minerAddressPublicKeyTextarea &&
        !elements.minerAddressPublicKeyTextarea.value.trim()
      ) {
        elements.minerAddressPublicKeyTextarea.value = senderPublicKey;
      }
    }
    // Error notification handled by apiClient
    addTxButton.disabled = false;
    addTxButton.innerHTML = originalButtonText;
  });
}

if (elements.miningForm) {
  elements.miningForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const mineButton = e.target.querySelector('button[type="submit"]');
    const originalButtonText = mineButton.innerHTML;

    if (!elements.minerAddressPublicKeyTextarea) return;

    const minerAddressPublicKey = elements.minerAddressPublicKeyTextarea.value;
    if (!minerAddressPublicKey.trim()) {
      showNotification(
        "Miner Reward Address (Public Key) is required and cannot be empty.",
        true
      );
      return;
    }

    // Check if there are any pending transactions
    const pendingTxCount = parseInt(document.getElementById('pending-tx-count').textContent);
    if (pendingTxCount === 0) {
      showNotification("No pending transactions to mine.", true);
      return;
    }

    mineButton.disabled = true;
    mineButton.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Initiating...';

    const miningModal = elements.miningModalEl
      ? bootstrap.Modal.getOrCreateInstance(elements.miningModalEl)
      : null;

    if (elements.miningAttemptsEl) elements.miningAttemptsEl.textContent = "0";
    if (elements.miningTimeEl) elements.miningTimeEl.textContent = "0.0s";
    if (elements.miningProgressEl) elements.miningProgressEl.style.width = "0%";
    if (miningModal) miningModal.show();

    mineButton.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Mining...';

    let attempts = 0;
    const startTime = Date.now();
    if (miningAnimationInterval) clearInterval(miningAnimationInterval);
    miningAnimationInterval = setInterval(() => {
      attempts++;
      if (elements.miningAttemptsEl)
        elements.miningAttemptsEl.textContent = attempts.toLocaleString();
      if (elements.miningTimeEl)
        elements.miningTimeEl.textContent =
          ((Date.now() - startTime) / 1000).toFixed(1) + "s";
      if (elements.miningProgressEl)
        elements.miningProgressEl.style.width = `${Math.min(
          95,
          (attempts % 100) * 0.95
        )}%`;
      if (elements.miningHashValueEl)
        elements.miningHashValueEl.textContent = Array.from(
          { length: 10 },
          () => Math.floor(Math.random() * 16).toString(16)
        ).join("");
    }, 60);

    const mineResult = await mineBlockAPI(minerAddressPublicKey);

    if (miningAnimationInterval) clearInterval(miningAnimationInterval);
    miningAnimationInterval = null;

    if (mineResult.success && mineResult.block) {
      if (elements.miningProgressEl)
        elements.miningProgressEl.style.width = "100%";
      if (elements.miningHashValueEl)
        elements.miningHashValueEl.textContent =
          mineResult.block.hash.substring(0, 10);

      setTimeout(() => {
        if (miningModal) miningModal.hide();
        showNotification(
          mineResult.message || `Block #${mineResult.block.index} mined!`
        );
      }, 1200);
    } else {
      if (miningModal) miningModal.hide();
      // Error notification handled by apiClient if mineResult.success is false
    }
    mineButton.disabled = false;
    mineButton.innerHTML = originalButtonText;
  });
}

// --- Other Action Buttons ---
if (elements.generateKeysBtn)
  elements.generateKeysBtn.addEventListener("click", generateAndStoreUserKeys);
if (elements.copyPkBtn)
  elements.copyPkBtn.addEventListener("click", copyPublicKeyToClipboard);

if (elements.validateChainBtn) {
  elements.validateChainBtn.addEventListener("click", async () => {
    elements.validateChainBtn.disabled = true;
    const result = await validateChainAPI();
    if (result) {
      showNotification(
        result.valid ? "Blockchain is VALID" : "Blockchain is INVALID!",
        !result.valid
      );
    } else {
      showNotification("Could not get validation status from server.", true);
    }
    elements.validateChainBtn.disabled = false;
  });
}

if (elements.saveChainBtn) {
  elements.saveChainBtn.addEventListener("click", async () => {
    elements.saveChainBtn.disabled = true;
    const result = await saveBlockchainAPI();
    if (result.success) {
      showNotification(
        result.message || "Blockchain state saved successfully!"
      );
    }
    elements.saveChainBtn.disabled = false;
    // Error notification handled by apiClient
  });
}

// --- Initial Load and Setup ---
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM fully loaded. Initializing application components.");
  loadUserKeys();
  initializeSocket();

  if (elements.infoModalEl) {
    const hasSeenInfoModal = localStorage.getItem(
      "hasSeenBlockchainInfoModal_v2"
    );
    if (!hasSeenInfoModal) {
      const infoModalInstance = bootstrap.Modal.getOrCreateInstance(
        elements.infoModalEl
      );
      infoModalInstance.show();
    }

    elements.infoModalEl.addEventListener("hidden.bs.modal", function () {
      localStorage.setItem("hasSeenBlockchainInfoModal_v2", "true");
      console.log(
        "Info modal hidden, 'hasSeenBlockchainInfoModal_v2' flag set."
      );
    });
  }
});
