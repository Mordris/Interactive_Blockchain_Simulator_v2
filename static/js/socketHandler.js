// static/js/socketHandler.js
import { showNotification } from "./utils.js";
import { handleBlockchainUpdateFromSocket } from "./uiUpdater.js";
// No direct call to initializeUserDirectory needed here anymore as handleBlockchainUpdateFromSocket covers it.

let socket; // Module-level socket instance

export function initializeSocket() {
  if (socket && socket.connected) {
    console.log("Socket already initialized and connected.");
    return;
  }

  socket = io({
    transports: ["websocket", "polling"], // Explicitly define transport preference
  });

  socket.on("connect", () => {
    console.log("Socket.IO: Connected to server!");
    showNotification(
      "Live connection to blockchain server established!",
      false
    );
    // Request initial state which includes blockchain data.
    // The handler for 'initial_state' will then call handleBlockchainUpdateFromSocket,
    // which in turn refreshes the user directory among other things.
    socket.emit("request_update", { reason: "Client initial connection" });
  });

  socket.on("disconnect", (reason) => {
    console.log("Socket.IO: Disconnected from server. Reason:", reason);
    // Attempt to reconnect is usually handled by Socket.IO client automatically
    // based on its configuration, but can be customized.
    showNotification(
      `Disconnected from server: ${reason}. Will attempt to reconnect.`,
      true
    );
  });

  socket.on("connect_error", (error) => {
    console.error("Socket.IO: Connection error:", error);
    showNotification(
      `Connection error: ${error.message}. Is the server running? Please refresh.`,
      true
    );
  });

  socket.on("initial_state", async (data) => {
    // Made async because handler is async
    console.log("Socket.IO: Received 'initial_state'", data);
    if (data && data.status) {
      // Basic check for valid data structure
      showNotification(
        data.status.message || "Initial blockchain state received.",
        false
      );
      await handleBlockchainUpdateFromSocket(data);
    } else {
      console.error(
        "Socket.IO: Received malformed 'initial_state' data:",
        data
      );
      showNotification("Received incomplete initial state from server.", true);
    }
  });

  socket.on("blockchain_updated", async (data) => {
    // Made async
    console.log("Socket.IO: Received 'blockchain_updated'", data);
    if (data && data.status) {
      // Basic check
      showNotification(
        data.status.message || "Blockchain has been updated!",
        false
      );
      await handleBlockchainUpdateFromSocket(data);
    } else {
      console.error(
        "Socket.IO: Received malformed 'blockchain_updated' data:",
        data
      );
      showNotification("Received incomplete update from server.", true);
    }
  });
}

// Function to manually request a full update via socket if needed from other modules
export function requestSocketUpdate(reason = "Manual UI request") {
  if (socket && socket.connected) {
    console.log("Socket.IO: Manually requesting update, reason:", reason);
    socket.emit("request_update", { reason: reason });
  } else {
    showNotification("Cannot request update: Not connected to server.", true);
  }
}
