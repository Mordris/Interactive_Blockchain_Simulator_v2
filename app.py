# app.py

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from blockchain import Blockchain
from transaction import Transaction
from utils.crypto_utils import generate_key_pair, sign_data
from predefined_users import get_public_user_info, PREDEFINED_USERS_DATA # For initial allocations
import json
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secure_and_random_secret_key_!@#' # Changed for best practice
socketio = SocketIO(app, cors_allowed_origins="*")

blockchain = None
FAUCET_GRANT_AMOUNT = 500.0
INITIAL_USER_ALLOCATION = 1000.0 # Amount for each predefined user

def perform_initial_setup_on_new_chain(bc_instance: Blockchain):
    """
    Called ONLY when a brand new blockchain (after genesis) is created.
    1. Allocates funds to predefined users.
    2. Mines these allocations into new blocks.
    """
    print("Performing initial setup: Allocating funds to predefined users...")
    if not PREDEFINED_USERS_DATA:
        print("No predefined users to allocate funds to.")
        return

    allocation_transactions = []
    for user_data in PREDEFINED_USERS_DATA:
        allocation_tx = Transaction(
            sender_public_key="GENESIS_ALLOCATION", # Special system sender
            recipient_public_key=user_data["public_key_pem"],
            amount=INITIAL_USER_ALLOCATION,
            signature=None # System transactions don't require signatures from this sender
        )
        allocation_transactions.append(allocation_tx)
        print(f"  + Staged allocation: {INITIAL_USER_ALLOCATION} coins to {user_data['name']}")

    if not allocation_transactions:
        return

    # Temporarily set these as the only pending transactions for focused mining
    original_pending_transactions = list(bc_instance.pending_transactions) # Save any existing (should be none for new chain)
    bc_instance.pending_transactions = allocation_transactions

    # Mine these allocation transactions.
    # The miner for these initial setup blocks could be a designated system address,
    # or for simplicity, the first predefined user can "mine" these setup blocks.
    initial_miner_pk = PREDEFINED_USERS_DATA[0]["public_key_pem"] if PREDEFINED_USERS_DATA else None
    if not initial_miner_pk: # Should not happen if PREDEFINED_USERS_DATA is populated
        _, initial_miner_pk = generate_key_pair() # Fallback dummy miner
        print(f"Warning: No predefined user to act as initial miner. Using dummy: {initial_miner_pk[:20]}...")

    mined_block_count = 0
    # Assuming mine_pending_transactions creates one block with all pending transactions.
    # If you had a max_tx_per_block, you'd loop here.
    if bc_instance.pending_transactions: # Make sure there's something to mine
        print(f"Mining initial allocation block(s) for {len(bc_instance.pending_transactions)} allocations...")
        block, _, _ = bc_instance.mine_pending_transactions(initial_miner_pk)
        if block:
            mined_block_count += 1
            print(f"  Mined allocation block #{block.index}")
        else:
            print("  ERROR: Failed to mine initial allocation block.")
    
    # Restore original pending transactions (should be empty if this is a truly new chain setup)
    bc_instance.pending_transactions = original_pending_transactions
    print(f"Initial setup complete. {mined_block_count} allocation block(s) mined.")


def init_blockchain():
    global blockchain
    try:
        blockchain = Blockchain.load_from_file()
        if blockchain is None: 
            print("No existing blockchain data found. Creating a new blockchain...")
            blockchain = Blockchain(difficulty=4) 
            blockchain.create_genesis_block()
            perform_initial_setup_on_new_chain(blockchain) # Allocate funds to predefined users
            blockchain.save_to_file() # Save the newly created chain with allocations
        print(f"Blockchain initialized: {blockchain}")
        if blockchain and blockchain.chain:
            print(f"Current chain length: {len(blockchain.chain)} blocks.")
    except Exception as e:
        print(f"CRITICAL ERROR during init_blockchain: {e}. Re-initializing a fresh blockchain.")
        traceback.print_exc()
        blockchain = Blockchain(difficulty=4)
        blockchain.create_genesis_block()
        perform_initial_setup_on_new_chain(blockchain) # Also allocate here on fresh creation due to error
        blockchain.save_to_file()
        print(f"Fresh blockchain created after error: {blockchain}")

init_blockchain()

def emit_blockchain_update(event_name="blockchain_updated", message=""):
    if blockchain is None: print("Error: Blockchain not initialized for emit."); return
    status = {'blocks': len(blockchain.chain), 'pending_transactions': len(blockchain.pending_transactions),
               'difficulty': blockchain.difficulty, 'mining_reward': blockchain.mining_reward, 'message': message}
    blocks_data = [{'index': b.index, 'timestamp': b.timestamp, 'transactions': b.transactions,
                    'previous_hash': b.previous_hash, 'hash': b.hash, 'nonce': b.nonce} for b in blockchain.chain]
    socketio.emit(event_name, {'status': status, 'blocks': blocks_data})
    print(f"Emitted {event_name}: Blk={status['blocks']}, PendTX={status['pending_transactions']}, Msg='{message}'")

@app.route('/')
def index_route(): return render_template('index.html')

@app.route('/api/keys/generate', methods=['POST'])
def api_generate_key_pair():
    priv, pub = generate_key_pair(); return jsonify({'success': True, 'private_key_pem': priv, 'public_key_pem': pub})

@app.route('/api/users/directory')
def get_user_directory_api():
    users_pub_info = get_public_user_info()
    users_with_balances = []
    if blockchain:
        for info in users_pub_info:
            try: users_with_balances.append({**info, "balance": blockchain.get_balance(info["public_key_pem"])})
            except Exception as e: print(f"Bal err for {info['name']}: {e}"); users_with_balances.append({**info, "balance": "Error"})
    else: users_with_balances = users_pub_info
    return jsonify(users_with_balances)

@app.route('/api/blockchain/create', methods=['POST'])
def create_blockchain_api():
    global blockchain
    data = request.json
    try:
        diff = int(data.get('difficulty', 2)); reward = float(data.get('mining_reward', 100.0))
        if not 1 <= diff <= 6: return jsonify({'success': False, 'error': 'Difficulty 1-6'}), 400
        if reward <= 0: return jsonify({'success': False, 'error': 'Mining reward > 0'}), 400
        
        print("API request to create NEW blockchain. Wiping existing state and re-allocating.")
        blockchain = Blockchain(difficulty=diff, mining_reward=reward)
        blockchain.create_genesis_block()
        perform_initial_setup_on_new_chain(blockchain) # Allocate funds to predefined users
        blockchain.save_to_file()
        msg = f'New blockchain (diff {diff}, reward {reward}) created with initial user funds.'
        emit_blockchain_update(message=msg)
        return jsonify({'success': True, 'message': msg})
    except Exception as e: traceback.print_exc(); return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/blockchain/balance') 
def get_address_balance_api():
    pk = request.args.get('key')
    print(f"--- Balance req for key: {pk[:30] if pk else 'None'}... ---")
    if not pk: return jsonify({'success': False, 'error': "Missing 'key' query param"}), 400
    try:
        if blockchain is None: return jsonify({'success': False, 'error': 'Blockchain not init'}), 500
        bal = blockchain.get_balance(pk)
        return jsonify({'success': True, 'public_key': pk, 'balance': bal})
    except Exception as e: traceback.print_exc(); return jsonify({'success': False, 'error': f"Bal err: {str(e)}"}), 500
    
@app.route('/api/blockchain/add-transaction', methods=['POST'])
def add_transaction_api():
    data = request.json
    try:
        tx = Transaction(data['sender_public_key'], data['recipient_public_key'], float(data['amount']), data['signature'])
        ok, msg, _ = blockchain.add_transaction(tx)
        if ok:
            blockchain.save_to_file(); emit_blockchain_update(message=msg)
            return jsonify({'success': True, 'message': msg})
        else: return jsonify({'success': False, 'error': msg}), 400
    except Exception as e: traceback.print_exc(); return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/blockchain/mine', methods=['POST'])
def mine_block_api():
    data = request.json
    try:
        # This miner_address_public_key is from the UI, representing the active browser user
        # who initiated the mining action. They get the reward.
        miner_pk_from_request = data['miner_address_public_key']
        if not miner_pk_from_request:
             return jsonify({'success': False, 'error': 'Miner reward address (public key) is required from client.'}), 400

        # The mine_pending_transactions function will create the reward tx for this miner
        block, duration, message_from_mine_logic = blockchain.mine_pending_transactions(miner_pk_from_request)
        
        if block:
            blockchain.save_to_file() # Save the new state
            # The emit_blockchain_update will send the new chain, status (incl. pending tx count = 0)
            # and the message will reflect the successful mining.
            # Balances (including miner's new reward and directory users) will be re-fetched by client
            # due to the 'blockchain_updated' event handled in uiUpdater.js.
            emit_blockchain_update(message=f"Block #{block.index} successfully mined by user.")
            return jsonify({
                'success': True, 
                'message': message_from_mine_logic, # Detailed message from the blockchain logic
                'block': { 
                    'index': block.index, 'hash': block.hash, 
                    'nonce': block.nonce, 'timestamp': block.timestamp 
                },
                'mining_duration': duration
            })
        else:
            # message_from_mine_logic contains the reason why no block was mined (e.g., "No user transactions")
            return jsonify({'success': False, 'error': message_from_mine_logic}) 
            
    except KeyError:
        return jsonify({'success': False, 'error': 'Missing miner_address_public_key field'}), 400
    except Exception as e:
        print(f"Error in /api/blockchain/mine: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/faucet/request-welcome-bonus', methods=['POST'])
def request_welcome_bonus_api():
    global blockchain
    data = request.json
    try:
        rcpt_pk = data['recipient_public_key']
        if not rcpt_pk: return jsonify({'success': False, 'error': 'Recipient PK required'}), 400
        
        print(f"Welcome bonus request for: {rcpt_pk[:20]}...")
        # Check if user already received a significant welcome bonus recently (optional, to prevent abuse)
        # For this simulator, we'll always grant it if the blockchain is new or user has 0.
        # The perform_initial_setup_on_new_chain should handle predefined users.
        # This faucet is more for the *browser user* who generates keys.

        grant_tx = Transaction("welcome_faucet", rcpt_pk, FAUCET_GRANT_AMOUNT, None)
        if not blockchain or not blockchain.get_latest_block(): return jsonify({'success': False, 'error': 'Blockchain not ready'}), 500
        
        original_pending = list(blockchain.pending_transactions)
        blockchain.pending_transactions = [grant_tx] # Focus on this grant
        
        # Reward for this faucet-triggered block also goes to the recipient
        mined_block, _, mine_msg = blockchain.mine_pending_transactions(rcpt_pk) 
        
        blockchain.pending_transactions.extend(original_pending) # Restore other pending TXs
        # A better way to restore if order matters or to avoid duplicates:
        # blockchain.pending_transactions = original_pending

        if mined_block:
            success_msg = f"{FAUCET_GRANT_AMOUNT} coins (plus mining reward) granted & mined for new user."
            blockchain.save_to_file(); emit_blockchain_update(message=success_msg)
            return jsonify({'success': True, 'message': success_msg})
        else: 
            blockchain.pending_transactions = original_pending # Ensure restoration on failure
            return jsonify({'success': False, 'error': f"Faucet auto-mine failed: {mine_msg}"}), 500
    except Exception as e: traceback.print_exc(); return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/utils/sign-data-for-client', methods=['POST'])
def client_sign_data_insecure_api(): # INSECURE: For demo only
    data = request.json
    try: sig = sign_data(data['private_key_pem'], data['data_to_sign']); return jsonify({'success': True, 'signature': sig})
    except Exception as e: return jsonify({'success': False, 'error': f"Signing err: {str(e)}"}), 400

@app.route('/api/blockchain/validate')
def validate_chain_api(): return jsonify({'valid': blockchain.is_chain_valid() if blockchain else False})

@app.route('/api/blockchain/save')
def save_blockchain_api():
    try: 
        if blockchain: blockchain.save_to_file(); return jsonify({'success': True, 'message': 'Blockchain saved.'})
        else: return jsonify({'success': False, 'error': 'No blockchain to save.'}), 500
    except Exception as e: traceback.print_exc(); return jsonify({'success': False, 'error': str(e)}), 500

@socketio.on('connect')
def handle_connect(): print('Client connected'); emit_blockchain_update('initial_state', "Initial state sent.")
@socketio.on('disconnect')
def handle_disconnect(): print('Client disconnected')
@socketio.on('request_update')
def handle_request_update(data): print(f"Update req: {data.get('reason')}"); emit_blockchain_update("Update on request.")

if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=True) # use_reloader can be helpful