# Interactive -->


## Features

- **Core Blockchain Logic:**
  - **Block Creation:** Implements `Block` objects Web-Based Blockchain Simulator v2

A Python and Flask web application that provides an interactive, visual simulation of a more with index, transactions, timestamp, previous hash, nonce, and SHA-256 hash.
  - ** complete blockchain including cryptographic key pairs, transaction signing, account balances, and a user directory. Users can generate wallets, createTransaction Management:**
    - `Transaction` objects now include `sender_public_key`, `recipient_public_ chains, add transactions, mine blocks, and observe the blockchain's state through a dynamic web interface.

## Screenshotskey`, `amount`, and a cryptographic `signature`.
    - Transactions are signed using ECDSA (simulated client-side via a backend utility for this demo).
    - Backend validation of transaction signatures and sender balances.
  - **Account

*(Consider adding updated screenshots reflecting the User Directory and other v2 features if you have them.)*

**Main Interface with User Balances:** The blockchain tracks and calculates the balance for each public key (address).
  - **Proof-of- Directory (Example):**
![Main Interface v2](./screenshots/main_v2.png)

**Transaction &Work (PoW):** Simple PoW algorithm; mining difficulty is configurable.
  - **Mining Rewards:** A Mining Flow (Example):**
![Transaction Flow v2](./screenshots/tx_flow_v2.png) configurable reward is granted to the miner's public key for successfully creating a block.
  - **Chain Validation:**


## Features

- **Core Blockchain Logic:**
  - **Block Creation:** Implements `Block` objects with Verifies hash links, data integrity, PoW, and transaction signatures for all blocks. System transactions (rewards, faucet, allocations index, transactions, timestamp, previous hash, nonce, and SHA-256 hash.
  - **Transaction Management:**
) are correctly handled without requiring signatures.
- **Wallet & User Simulation:**
  - **Browser User Wallet:**
    - `Transaction` objects now include `sender_public_key`, `recipient_public_key`, `amount    - Client-side generation of ECDSA public/private key pairs (PEM format).
    - Keys are stored`, and a cryptographic `signature`.
    - Transactions are signed using ECDSA (simulated client-side via a in browser `localStorage` for the active user.
    - Automatic "Welcome Bonus" of coins (via a Faucet mechanism backend utility for this demo).
    - Backend validation of transaction signatures and sender balances.
  - **Account Bal that auto-mines a block) when new keys are generated.
  - **Predefined User Directory:**
    ances:** The blockchain tracks and calculates the balance for each public key (address).
  - **Proof-of-Work (- A list of ~5-10 predefined users with their own generated public keys.
    - The UI displaysPoW):** Simple PoW algorithm; mining difficulty is configurable.
  - **Mining Rewards:** A configurable reward is granted these users, their (shortened) public keys, and their current balances, updated in real-time.
    - Ability to the miner's public key for successfully creating a block.
  - **Chain Validation:** Verifies hash links, data to easily copy a directory user's public key or populate it into transaction/mining forms.
  - **Initial Allocations:** integrity, PoW, and transaction signatures for all blocks. System transactions (rewards, faucet, allocations) are correctly handled Predefined users automatically receive an initial allocation of coins when a new blockchain is created.
- **Flask Web Backend:** without requiring signatures.
- **Wallet & User Simulation:**
  - **Browser User Wallet:**
    - Client
  - **RESTful API & SocketIO:**
    - Exposes endpoints for key generation, user directory,-side generation of ECDSA public/private key pairs (PEM format).
    - Keys are stored in browser `localStorage` for balance checks, creating chains, adding transactions, mining, validation, and saving.
    - Utilizes Flask-Socket the active user.
    - Automatic "Welcome Bonus" of coins (via a Faucet mechanism that auto-mines a blockIO for real-time updates to all connected clients (blockchain status, new blocks, user directory balances).
  -) when new keys are generated.
  - **Predefined User Directory:**
    - A list of predefined users with their own **Serves Frontend:** Delivers HTML, CSS, and modular JavaScript.
- **Interactive Web Frontend (Modular JavaScript):** generated public keys.
    - The UI displays these users, their (shortened) public keys, and their current
  - **Dynamic Updates:** Uses SocketIO for real-time UI updates without page reloads. JavaScript is organized into modules (` balances, updated in real-time.
    - Ability to easily copy a directory user's public key or populate it into transactionapiClient.js`, `keyManager.js`, `uiUpdater.js`, `socketHandler.js`, `utils.js/mining forms.
  - **Initial Allocations:** Predefined users automatically receive an initial allocation of coins when a`, `app.js`).
  - **Visual Blockchain Display:** Renders blocks and their transactions, including system transactions like rewards and new blockchain is created.
- **Flask Web Backend:**
  - **RESTful API & SocketIO:**
    - Ex allocations.
  - **Status Dashboard:** Shows current block count, pending transactions, difficulty, and mining reward.
poses endpoints for key generation, user directory, balance checks, creating chains, adding transactions, mining, validation, and saving  - **Forms for Interaction:** Allows users to add transactions (signing with their active key) and initiate mining (specifying reward address.
    - Utilizes Flask-SocketIO for real-time updates to all connected clients (blockchain status, new).
  - **Mining Animation:** Provides visual feedback during the PoW mining process.
  - **Information Modal blocks, user directory balances).
  - **Serves Frontend:** Delivers HTML, CSS, and modular JavaScript.
- **:** A "How to Use" guide is presented to users on their first visit (tracked via `localStorage`).
  - **Interactive Web Frontend (Modular JavaScript):**
  - **Dynamic Updates:** Uses SocketIO for real-time UI updatesToast Notifications:** Displays success and error messages.
  - **Responsive Design:** Uses Bootstrap for a clean and responsive layout without page reloads. JavaScript is organized into modules.
  - **Visual Blockchain Display:** Renders blocks and their transactions..
- **Persistence:**
  - The blockchain state (chain, pending transactions, difficulty, mining reward) is
  - **Status Dashboard:** Shows current block count, pending transactions, difficulty, and mining reward.
  - ** saved to `blockchain_data.json` on the server.
  - The application loads this state on startup.
  - Users can explicitly save the current state via a UI button.
- **Security Note (Simulation Context):Forms for Interaction:** Allows users to add transactions and initiate mining.
  - **Mining Animation:** Provides visual feedback during the Po**
  - For simplicity in this demo, transaction signing by the browser user involves sending the private key to a backend utility (`/W mining process.
  - **Information Modal:** A "How to Use" guide is presented on first visit.
api/utils/sign-data-for-client`). **In a real-world application, private keys must NEVER leave the  - **Toast Notifications:** Displays success and error messages.
  - **Responsive Design:** Uses Bootstrap.
- **Persistence client device.** True client-side signing would require a JavaScript cryptographic library. This is clearly noted in the "How to:**
  - Blockchain state is saved to `blockchain_data.json` on the server.
  - The application Use" modal.

## Requirements

- Python 3.8+ (due to type hinting like `list[ loads this state on startup.
- **Security Note (Simulation Context):**
  - For simplicity, transaction signing by thedict]`)
- Pip (Python package installer)
- Flask
- Flask-SocketIO
- python-dotenv
- browser user involves sending the private key to a backend utility. **In a real-world application, private keys must NEVER leave pycryptodomex (for ECDSA cryptography)

Install dependencies using:

pip install -r requirements.txt

The `requirements.txt` file lists necessary Python packages


## Setup and Running

Follow these steps to set0.2
flask-cors==4.0.0
python-dotenv==1.0.1
 up and run the Blockchain Simulator on your local machine:

1.  **Prerequisites:**
    *   PythonFlask-SocketIO==5.3.6
pycryptodomex==3.23.0
``` 3.8 or higher installed.
    *   `pip` (Python package installer) available.
    *   A modern web browser (e.g., Chrome, Firefox, Edge).

2.  **Clone or

## Setup and Running

Follow these steps to set up and run the Blockchain Simulator on your local machine:

1.  ** Download the Project:**
    Obtain all project files and place them in a single directory on your computer.

3.  **Clone or Download the Project:**
    Obtain all project files and place them in a single directory.

2.  Populate Predefined User Keys (CRUCIAL FIRST STEP):**
    *   The simulation uses a set of**Populate Predefined User Keys (CRUCIAL FIRST STEP):**
    *   The simulation uses a set of predefined users. You need to generate cryptographic key pairs for them.
    *   Navigate to your project directory in the predefined users. You need to generate cryptographic key pairs for them.
    *   Navigate to your project directory in the terminal.
    *   Run the script:
        ```
        python3 predefined_users.py
        ```
 terminal.
    *   Run the script:
        ```bash
        python3 predefined_users.py
    *   This script will print out sample PEM-formatted public and private key pairs to your console.
    *        ```
    *   This script will print sample PEM-formatted public and private key pairs.
    *   Open   Open the `predefined_users.py` file in a text editor.
    *   Carefully copy `predefined_users.py` in a text editor.
    *   Copy the generated **full public and private PEM the **full public and private PEM strings** generated by the script into the `PREDEFINED_USERS_DATA` list within strings** into the `PREDEFINED_USERS_DATA` list, replacing placeholders. Ensure you have several unique users. The `predefined_users.py`, replacing any existing placeholder keys. Ensure you have at least 5 unique users (the script can help generate more if needed by modifying the `num_to_generate` variable within its `if __name script provides formatted output for easy copy-pasting.
    *   **Important:** The application relies on these actual keys__ == '__main__':` block).
    *   **Important:** The application relies on these actual keys for cryptographic. Using non-functional placeholders will cause errors. The provided `predefined_users.py` includes 5 sample ( operations. Using non-functional placeholder text will cause errors.

4.  **Create and Activate a Python Virtual Environment (but functional) key pairs to start with.

3.  **Create and Activate a Python Virtual Environment (Recommended):Recommended):**
    Open your terminal/command prompt in the project's root directory.
    ```
    **
    In the project's root directory:
    ```bash
    python3 -m venv venvpython3 -m venv venv
    ```
    Activate the environment:
    *   **macOS
    ```
    Activate the environment:
    *   **macOS/Linux:**
        ```bash
/Linux:**
        ```
        source venv/bin/activate
        ```
    *   **Windows (Command Prompt        source venv/bin/activate
        ```
    *   **Windows (Command Prompt):**
        ):**
        ```
        venv\Scripts\activate.bat
        ```
    *   **Windows (```bash
        venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
PowerShell):**
        ```
        venv\Scripts\Activate.ps1
        ```
        (If        ```powershell
        venv\Scripts\Activate.ps1
        ```
        (If PowerShell script execution is disabled PowerShell script execution is disabled, you may need to run `Set-ExecutionPolicy Unrestricted -Scope Process` first in that, you may need to run `Set-ExecutionPolicy Unrestricted -Scope Process` first.)
    Your terminal prompt PowerShell session.)
    Your terminal prompt should change to indicate the virtual environment is active (e.g., `(venv)` should change (e.g., show `(venv)`).

4.  **Install Dependencies:**
    With).

5.  **Install Dependencies:**
    With the virtual environment activated, install the required Python packages:
    ```
    pip install -r requirements.txt
    ```
    *(If you encounter issues with `py the virtual environment activated:
    ```bash
    pip install -r requirements.txt
    ```

5.  **cryptodomex` on Linux, you might need to install system build tools like `gcc` and `python3-dev`.Run the Flask Web Application:**
    ```bash
    python3 app.py
    ```
    The server On Windows, ensure you have appropriate C++ build tools available, though pre-built wheels usually avoid this need.)*

6 will start, typically logging messages. By default, it runs on `http://127.0.0.1:5.  **Run the Flask Web Application:**
    Execute the main application script:
    ```
    python3 app.000/`.

6.  **Open in Browser:**
    Navigate to `http://127py
    ```
    The server will start, typically logging messages to your console. It will indicate if it's loading existing.0.0.1:5000/`.

7.  **Interact with the Simulator:**
    *   The "How to Use" modal should appear on your first visit.
    *   Click **"Generate My Keys blockchain data or creating a new one (including allocating initial funds to predefined users). By default, it runs on `http://127.0.0.1:5000/`.

7.  **Open in Browser"** in "Your Active Wallet" to create your identity and receive a welcome bonus.
    *   Explore the **:**
    Navigate to `http://127.0.0.1:5000/`User Directory** to see predefined users and their balances.
    *   Use the forms to **Add Transactions** and ** in your preferred web browser.

8.  **Interact with the Simulator:**
    *   The "How to UseMine Blocks**.
    *   Observe real-time updates.
    *   Utilize navbar actions for **New Chain**," information modal should appear on your first visit.
    *   Begin by clicking **"Generate My Keys"** **Validate**, and **Save**.

## How It Works - Key Features

*   **Signed Transactions:** Transactions are cryptographically in the "Your Active Wallet" panel. This creates your identity for interacting with the simulation and grants you a welcome bonus. signed and verified.
*   **Balance System:** Account balances are tracked and enforced.
*   **Real-
    *   Explore the **User Directory** to see predefined users and their balances.
    *   Use the forms to **time Updates with SocketIO:** Blockchain state changes are pushed to clients.
*   **Initial State for Users:** PreAdd Transactions** and **Mine Blocks**.
    *   Observe real-time updates to the **Blockchain Status**, **defined users and new browser users receive initial coin allocations/bonuses.
*   **Modular JavaScript:** Frontend logic is organized forBlockchain Visualizer**, and user balances via SocketIO.
    *   Utilize the navbar actions for **New Chain better maintainability.

## Developer Notes

*   **Client-Side Signing Simulation:** The `/api/utils/**, **Validate**, and **Save**.

## How It Works - Key Features

*   **Signed Transactions:** Transactions are cryptographically signed by the sender's private key (simulated for the browser user via a backend utility) and verified by thesign-data-for-client` endpoint is for demonstration purposes and is insecure for production.
*   **Error Handling:** blockchain.
*   **Balance System:** The `blockchain.py` module calculates and enforces account balances, preventing over Basic error handling is implemented.
*   **Scalability:** This is a single-node simulator.
*   **spending.
*   **Real-time Updates with SocketIO:** Changes to the blockchain state (new blocks, newDifficulty Adjustment:** Mining difficulty is fixed upon chain creation.

## Future Enhancements

*   Implement true client-side JavaScript signing.
*   Allow users to "log in" as predefined users.
*   Dynamic difficulty adjustment.
 pending transactions) are immediately pushed to all connected clients. User directory balances are also refreshed.
*   **Initial State for Users:***   Transaction fees.
*   Unit and Integration tests.

``` Predefined users in `predefined_users.py` are automatically given an initial coin allocation when a new blockchain is created