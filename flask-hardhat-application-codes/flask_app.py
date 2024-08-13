from flask import Flask, request, render_template, g
import sqlite3
from web3 import Web3

app = Flask(__name__)
DATABASE = 'contracts.db'

# ABI i adresa pametnog ugovora
contract_abi = [ 'ABI OVDE'
]
contract_address = 'UGOVOR OVDE'

# Povezivanje sa lokalnim Ethereum cvorom
web3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
print(f"Web3 is connected: {web3.is_connected()}")

# Proveri da li je web3 povezan
if not web3.is_connected():
    raise Exception("Ne moze se povezati sa Ethereum cvorom")

# Funkcija za povezivanje sa bazom podataka
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Postavi vrednost na 0 prilikom startovanja aplikacije
def initialize_database():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            address TEXT PRIMARY KEY,
            value INTEGER
        )
    ''')
    
    # Postavi vrednost na 0
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    try:
        contract.functions.set(0).transact({'from': web3.eth.accounts[0]})
        print("Initial value set to 0")
    except Exception as e:
        print(f"Error setting initial value in contract: {e}")
    
    # Inicijalizuj vrednost u bazi
    conn.execute('INSERT OR REPLACE INTO contracts (address, value) VALUES (?, ?)',
                 (contract_address, 0))
    conn.commit()
    conn.close()

def get_contract_value():
    conn = get_db_connection()
    contract = conn.execute('SELECT * FROM contracts WHERE address = ?', (contract_address,)).fetchone()
    conn.close()
    return contract['value'] if contract else 'No value found'

def set_contract_value(value):
    conn = get_db_connection()
    try:
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
        tx_hash = contract.functions.set(int(value)).transact({'from': web3.eth.accounts[0]})
        conn.execute('UPDATE contracts SET value = ? WHERE address = ?', (value, contract_address))
        conn.commit()
        conn.close()
        return tx_hash.hex()
    except Exception as e:
        return f'Error setting value in contract: {e}'

@app.route('/')
def index():
    current_value = get_contract_value()
    return render_template('index.html', current_value=current_value)

# XSS vulnerability
@app.route('/xss', methods=['GET', 'POST'])
def xss():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '')
        return render_template('xss.html', user_input=user_input)
    return render_template('xss_form.html')

# CSRF vulnerability
@app.route('/csrf_form')
def csrf_form():
    return render_template('csrf_form.html')

@app.route('/csrf_post', methods=['POST'])
def csrf_post():
    csrf_value = request.form.get('csrf_value', '')
    set_contract_value(csrf_value)
    return render_template('csrf_post.html', value=get_contract_value())

# JavaScript Hijacking (Example Interaction)
@app.route('/interact')
def interact():
    return render_template('interact.html')

@app.route('/set_value', methods=['POST'])
def set_value():
    value = request.form.get('value')
    tx_hash = set_contract_value(value)
    return f'Transaction Hash: {tx_hash}'

# Stranica podlo┼żna SQL injekciji
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        address = request.form['address']
        conn = get_db_connection()
        # Ovaj upit je podlo┼żan SQL injekciji
        query = f"SELECT * FROM contracts WHERE address = '{address}'"
        result = conn.execute(query).fetchall()
        conn.close()
        return render_template('search_results.html', result=result)
    return render_template('search_form.html')

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
