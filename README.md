# Interactive Web-Based Blockchain Simulator v2

A Python and Flask web application that provides an interactive, visual simulation of a more complete blockchain. This version includes features like cryptographic key pairs for users, transaction signing, account balance tracking, a predefined user directory with initial fund allocations, and real-time updates via WebSockets. Users can generate their own wallets, create new blockchain instances, add transactions between accounts, mine blocks to confirm transactions and earn rewards, validate the chain's integrity, and save the blockchain state.

## Screenshots

_(Consider adding 1-2 updated screenshots reflecting the User Directory, wallet interactions, and the overall UI. If you don't have them ready, you can add them later or omit this section for now.)_

**Example: Main Interface with User Directory:**

<!-- ![Main Interface v2](./screenshots/main_v2.png) -->

_(Screenshot placeholder)_

**Example: Transaction & Mining Flow:**

<!-- ![Transaction Flow v2](./screenshots/tx_flow_v2.png) -->

_(Screenshot placeholder)_

## Features

The simulator boasts a comprehensive set of features to illustrate core blockchain concepts:

**Core Blockchain Logic:**

- **Blocks & Chaining:** Implements `Block` objects with index, a list of transactions, timestamp, the hash of the preceding block, a nonce for Proof-of-Work, and its own SHA-256 hash.
- **Transaction Management:**
  - `Transaction` objects include `sender_public_key`, `recipient_public_key`, `amount`, and a cryptographic `signature`.
  - Transactions are signed using ECDSA (P-256 curve).
  - The backend validates transaction signatures and ensures senders have sufficient balances before adding transactions to the pending pool.
- **Account Balances:** The system tracks and calculates the current coin balance for each public key (address) by iterating through confirmed and pending transactions.
- **Proof-of-Work (PoW):** Includes a simple PoW algorithm where miners search for a nonce that results in a block hash with a configurable number of leading zeros. Mining difficulty can be set when creating a new chain.
- **Mining Rewards:** A configurable coin reward is granted to the miner's public key for successfully mining and adding a new block to the chain.
- **Chain Validation:** Provides a mechanism to verify the entire blockchain's integrity, checking:
  - Correctness of the Genesis Block.
  - Integrity of hash links between blocks.
  - Validity of Proof-of-Work for each block.
  - Validity of all transaction signatures within each block (excluding system-generated transactions).

**Wallet & User Simulation:**

- **Active User Wallet (Browser-Side):**
  - Client-side generation of ECDSA public/private key pairs (PEM format) for the person using the simulator.
  - Generated keys are stored in the browser's `localStorage` for persistence during the session.
  - New browser users automatically receive a "Welcome Bonus" of coins (via a Faucet mechanism that auto-mines a block) upon first key generation.
- **Predefined User Directory:**
  - Includes a set of predefined simulated users, each with their own pre-generated public key.
  - The UI displays this directory, showing each user's name, a shortened version of their public key, and their current coin balance.
  - Balances in the directory are updated in real-time reflecting blockchain changes.
  - Provides easy one-click actions to copy a directory user's public key or populate it into the "Recipient" or "Miner Reward Address" fields in forms.
- **Initial Allocations for Predefined Users:**
  - When a new blockchain is created (either on first server start or via the "New Chain" UI option), predefined users automatically receive a significant initial allocation of coins, mined into an early block.

**Flask Web Backend & Communication:**

- **API Endpoints:** Exposes RESTful API endpoints for functionalities such as:
  - Generating key pairs for the active user.
  - Retrieving the user directory with current balances.
  - Fetching the balance of any specific public key.
  - Creating a new blockchain instance with custom difficulty/reward.
  - Adding new (signed) transactions to the pending pool.
  - Initiating the mining of a new block.
  - Validating the current blockchain.
  - Saving the current blockchain state to a file.
  - A Faucet endpoint for the "Welcome Bonus".
  - A (simulation-only, insecure) utility endpoint for signing data on behalf of the client.
- **Real-time Updates with SocketIO:** Utilizes Flask-SocketIO to push real-time updates to all connected web clients when the blockchain state changes (e.g., a new block is mined, a transaction is added to pending, a new chain is created). This keeps the UI (dashboard, blockchain display, user balances) synchronized.

**Interactive Web Frontend (Modular JavaScript):**

- **Dynamic User Interface:** The UI is built with HTML, Bootstrap 5, and custom CSS. All interactions and data displays are managed by JavaScript without requiring full page reloads.
- **Modular JavaScript:** Client-side code is organized into modules (`apiClient.js`, `keyManager.js`, `uiUpdater.js`, `socketHandler.js`, `utils.js`, and `app.js` as the main orchestrator) for better structure and maintainability.
- **Visual Blockchain Display:** Dynamically renders the chain of blocks, showing key details for each block and a list of its transactions.
- **Status Dashboard:** Displays live information: total blocks, number of pending transactions, current mining difficulty, and the standard mining reward.
- **Interactive Forms:**
  - "Add Transaction": Allows the active user to specify a recipient (by pasting a key or selecting from the directory) and an amount.
  - "Mine Block": Allows the user to initiate mining. The reward address defaults to the active user's key but can be changed to any valid public key.
- **Mining Animation:** A modal dialog provides visual feedback during the Proof-of-Work mining process, showing simulated attempts and elapsed time.
- **Information Modal:** A "How to Use" guide is automatically presented to users on their first visit (tracked via `localStorage`) and can be accessed anytime via a navbar button.
- **Toast Notifications:** Non-intrusive pop-up messages provide feedback for actions (e.g., transaction added, block mined, errors).

**Persistence:**

- The entire blockchain state (chain of blocks, current pending transactions, difficulty, and mining reward settings) is saved to a `blockchain_data.json` file on the server.
- The application automatically loads this state upon startup if the file exists.
- A "Save Chain" button in the UI allows the user to explicitly trigger saving the current state.

**Simulation Context & Notes:**

- **Client-Side Signing Simulation:** For simplicity in this educational demo, the process of the browser user signing a transaction involves sending their private key to a dedicated backend utility endpoint (`/api/utils/sign-data-for-client`). **It is CRITICALLY IMPORTANT to understand that in a real-world, secure blockchain application, the private key MUST NEVER leave the client's device or browser.** True client-side signing would necessitate using a JavaScript cryptographic library (e.g., `jsrsasign`, Web Crypto API) directly in the browser. This simulation approach is clearly noted in the "How to Use" modal.

## Requirements

To run this Blockchain Simulator, you will need the following software installed:

- **Python:** Version 3.8 or higher (due to modern type hinting like `list[dict]`).
- **pip:** The Python package installer (usually comes with Python).
- **A modern web browser:** Such as Google Chrome, Mozilla Firefox, or Microsoft Edge.

The specific Python package dependencies are listed in the `requirements.txt` file:

flask==3.0.2
flask-cors==4.0.0
python-dotenv==1.0.1
Flask-SocketIO==5.3.6
pycryptodomex==3.23.0

- **Flask:** A micro web framework for Python, used to build the backend server and API.
- **Flask-SocketIO:** Enables real-time, bidirectional communication between the web clients and the server.
- **python-dotenv:** Used for managing environment variables (though not explicitly used for critical config in this version, it's good practice).
- **pycryptodomex:** A powerful cryptographic library used for generating ECDSA key pairs, signing transactions, and verifying signatures.
- **Flask-CORS:** (Cross-Origin Resource Sharing) Included for flexibility, though with the frontend served from the same origin, strict CORS policies might not be an immediate issue.

## Setup and Running

Follow these steps to set up and run the Blockchain Simulator on your local machine:

1.  **Clone or Download the Project:**
    Obtain all project files and place them in a single directory on your computer.

2.  **Populate Predefined User Keys (CRUCIAL FIRST STEP):**
    The simulation includes a directory of predefined users who are automatically allocated initial funds. You need to generate actual cryptographic key pairs for them.

    - Navigate to your project's root directory in your terminal/command prompt.
    - Run the utility script provided within `predefined_users.py` to generate sample key pairs:
      ```bash
      python3 predefined_users.py
      ```
    - This script will print PEM-formatted public and private key pairs to your console.
    - Open the `predefined_users.py` file in a text editor.
    - Carefully copy the **full public and private PEM strings** for several users (e.g., 5 to 10) from the script's output into the `PREDEFINED_USERS_DATA` list within this file, replacing any existing placeholder examples. Ensure each user entry has a unique name and correctly corresponding public and private keys. The script at the bottom of `predefined_users.py` can be modified to generate more pairs if needed.
    - **Important:** The application relies on these being actual, valid PEM keys for cryptographic operations. Using malformed or non-functional placeholder text will lead to errors. The file is initialized with 5 sample (but functional) key pairs to get you started.

3.  **Create and Activate a Python Virtual Environment (Highly Recommended):**
    This isolates the project's dependencies from your global Python installation. In your project's root directory:

              ```bash
              python3 -m venv venv
              ```

              Activate the environment:

              - **macOS/Linux:**
                ```bash
                source venv/bin/activate
                ```
              - **Windows (Command Prompt):**
                ```bash
                venv\Scripts\activate.bat
                ```
              - **Windows (PowerShell):**
                `powershell

        venv\Scripts\Activate.ps1
        `      _(If PowerShell script execution is disabled, you might need to run`Set-ExecutionPolicy Unrestricted -Scope Process`first in that PowerShell session.)_

    Your terminal prompt should change (e.g., show`(venv)`) to indicate the virtual environment is active.

4.  **Install Dependencies:**
    With the virtual environment activated, install the required Python packages using the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

    _(Note: If you encounter issues installing `pycryptodomex` on Linux, you might need system build tools like `gcc` and `python3-dev`. On Windows, ensure you have appropriate C++ build tools from Microsoft, although pre-built wheels for `pycryptodomex` usually prevent this necessity.)_

5.  **Run the Flask Web Application:**
    Execute the main application script from your project's root directory:

    ```bash
    python3 app.py
    ```

    The server will start, and you should see log messages in your console, including:

    - Initialization of the blockchain (either loading from `blockchain_data.json` or creating a new one).
    - If a new blockchain is created, messages about the "Genesis Block" and "Initial Allocations" for predefined users being processed and mined.
    - The URLs where the application is accessible (typically `http://127.0.0.1:5000/`).

6.  **Open in Browser:**
    Navigate to `http://127.0.0.1:5000/` in your preferred web browser.

7.  **Interact with the Simulator:**
    - Upon your first visit, a "How to Use" information modal will automatically appear. Read through it to understand the simulator's features.
    - **Generate Your Keys:** The first step is usually to click the **"Generate My Keys"** button in the "Your Active Wallet" panel. This creates your unique identity for the simulation, stores your keys in the browser's local storage, and grants you an automatic "Welcome Bonus" of coins.
    - **Explore the User Directory:** View the list of predefined users and their initial coin balances. You can click on a user's name to populate their public key into the "Miner Reward Address" field, or click on their shortened public key to populate the "Recipient Public Key" field for transactions. A copy icon next to each allows copying their full public key.
    - **Add Transactions:** Use your active wallet to send coins to users from the directory or any other valid public key.
    - **Mine Blocks:** Initiate the mining process. You can specify the miner reward address (it defaults to your active wallet's key).
    - Observe real-time updates to the "Blockchain Status" dashboard, the "Blockchain Visualizer," and balances in the "User Directory" via SocketIO.
    - Utilize the navbar actions: "How to Use," "New Chain" (to reset and reinitialize the blockchain), "Validate" (to check chain integrity), and "Save" (to persist the current blockchain state to the server's `blockchain_data.json` file).

## How It Works - Key Features

This simulator demonstrates several fundamental blockchain mechanisms:

- **Cryptographic Security:** Transactions are secured using ECDSA digital signatures. Each user (including the active browser user and predefined directory users) has a public-private key pair. Transactions are signed with the sender's private key and can be verified by anyone using the sender's public key.
- **Decentralized Ledger (Simulated):** While running on a single server, the application simulates a chain of blocks. Each block contains a hash of the previous block, creating an immutable, ordered record of transactions.
- **Proof-of-Work (PoW):** New blocks are added to the chain through a mining process that requires computational effort (solving a PoW puzzle). This difficulty is configurable.
- **Account Balances:** The system maintains and updates the coin balance for each public key (address) based on confirmed transactions in the blockchain and considers pending transactions for the active user's spendable balance.
- **Real-time Interaction:** Flask-SocketIO enables live updates to all connected clients. When a new block is mined or a transaction is added to the pending pool, the UI reflects these changes immediately without needing a page refresh. This includes updates to the blockchain visualizer, status dashboard, and user balances.
- **Initial Coin Distribution:**
  - **Predefined Users:** Receive an automatic, substantial coin allocation when a new blockchain is created, ensuring they have funds to participate in the simulation from the start.
  - **Active Browser User:** Receives a "Welcome Bonus" via an automated faucet mechanism when they first generate their keys, allowing them to begin transacting quickly.
- **Modular Design:** The backend (Python/Flask) and frontend (JavaScript) are structured with a separation of concerns. The JavaScript is further broken down into modules for better organization (API client, key management, UI updates, WebSocket handling, utilities).
- **Data Persistence:** The state of the blockchain (blocks, pending transactions, settings) is saved to a `blockchain_data.json` file on the server, allowing the simulation state to persist between server restarts.

**Important Simulation Note:** For educational simplicity, when the browser user "signs" a transaction, their private key is sent to a backend utility for the signing operation. In a real-world secure blockchain application, the private key **must never** leave the user's client-side environment. True client-side signing would be implemented using JavaScript cryptographic libraries directly within the browser.

## Developer Notes

- **Python Backend:** Built with Flask and Flask-SocketIO.
  - `app.py`: Main application file, routes, SocketIO handlers.
  - `blockchain.py`, `block.py`, `transaction.py`: Core blockchain logic.
  - `utils/crypto_utils.py`: Cryptographic operations (key generation, signing, verification) using `pycryptodomex`.
  - `predefined_users.py`: Contains data for simulated users, including their pre-generated key pairs. **Remember to populate this with actual keys if starting from scratch.**
- **JavaScript Frontend:** Modular structure located in `static/js/`.
  - `app.js`: Main orchestrator, event listeners.
  - `apiClient.js`: Handles all `fetch` requests to backend API endpoints.
  - `keyManager.js`: Manages the active browser user's keys (generation, localStorage, UI updates for key display).
  - `uiUpdater.js`: Contains functions for updating various parts of the DOM (dashboard, blockchain display, user directory, active user balance).
  - `socketHandler.js`: Initializes and manages SocketIO client-side event handling, triggering UI updates.
  - `utils.js`: Common utility functions (notifications, formatting).
- **Client-Side Signing Simulation:** The endpoint `/api/utils/sign-data-for-client` is used to simulate transaction signing. The browser user's private key is sent to this endpoint. **This is insecure and purely for demonstration purposes.** In a production environment, private keys must never leave the client, and signing would be performed in the browser using JavaScript crypto libraries.
- **Error Handling:** Basic error handling is implemented, with toast notifications for users and console logs for developers. Server-side exceptions include tracebacks in the console when `debug=True`.
- **Initial Data:**
  - If `blockchain_data.json` is not found on server start, a new blockchain is created.
  - This new chain includes a genesis block, followed by a block (or blocks) containing initial coin allocations for users defined in `predefined_users.py`.
  - The active browser user receives a "Welcome Bonus" (auto-mined block) upon generating their keys for the first time via the UI.
- **Dependencies:** Managed via `requirements.txt`. Uses `pycryptodomex` for cryptography.
- **Development Server:** The application is run using Flask's development server with SocketIO support (`socketio.run(app, debug=True, ...)`). For production, a more robust WSGI server like Gunicorn with `eventlet` or `gevent` workers would be necessary for Flask-SocketIO. The `AssertionError: write() before start_response` seen occasionally in the logs is often an artifact of the development server's handling of WebSocket upgrades and auto-reloading.

## Future Enhancements

This simulator provides a solid foundation. Potential areas for future development and enhancement include:

- **True Client-Side Signing:** Implement transaction signing directly in the browser using JavaScript cryptographic libraries (e.g., `jsrsasign`, Web Crypto API) to ensure private keys never leave the client device. This would be a critical step towards a more secure and realistic model.
- **User Account Management/Selection:**
  - Allow users to create and manage multiple wallets/identities within the browser.
  - Enable users to "act as" or "log in" with one of the predefined user accounts from the directory to initiate transactions from their perspective.
- **Dynamic Difficulty Adjustment:** Implement an algorithm where the mining difficulty automatically adjusts based on the average time taken to mine previous blocks, aiming for a consistent block time.
- **Transaction Fees:** Introduce optional transaction fees that users can include to incentivize miners. Miners would then collect these fees in addition to the block reward.
- **Block Size Limits & Mempool Prioritization:** Simulate a maximum block size and have miners prioritize transactions from the mempool (e.g., based on fees or age).
- **Enhanced Network Simulation (Advanced):**
  - Explore concepts of multiple nodes.
  - Simulate transaction and block propagation between nodes.
  - Introduce a simplified consensus mechanism (e.g., longest chain rule).
- **More Sophisticated Wallet UI:**
  - Display transaction history for the active wallet.
  - Visual import/export of keys (for simulation purposes).
- **Smart Contracts (Very Advanced):** Introduce a basic scripting or smart contract capability to transactions.
- **Improved UI/UX:**
  - More detailed block and transaction explorers.
  - Visualizations of the Merkle tree if implemented.
  - Enhanced animations and user feedback.
- **Comprehensive Testing:** Develop a suite of unit and integration tests using frameworks like `pytest` to ensure code correctness and prevent regressions.
- **API Documentation:** Use tools like Swagger/OpenAPI (e.g., via Flask-RESTx or Connexion) to generate interactive API documentation.
- **Containerization:** Provide a `Dockerfile` for easy deployment and environment consistency.

## License

This project is open-source and licensed under the MIT License.

Copyright (c) 2025 Yunus Emre Gültepe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
