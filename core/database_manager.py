import sqlite3
import time
from config import DATABASE_NAME, GAME_COST

def init_db():
    """Inicializa o banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            force REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machine_state (
            id INTEGER PRIMARY KEY CHECK (id = 1), -- Garante apenas uma linha
            current_state TEXT NOT NULL,
            credits INTEGER NOT NULL DEFAULT 0,
            last_punch_time DATETIME,
            message TEXT
        )
    ''')
    # Initialize with IDLE state if not present
    cursor.execute("INSERT OR IGNORE INTO machine_state (id, current_state, credits, message) VALUES (1, 'IDLE', 0, 'Machine is idle.')")
    conn.commit()
    conn.close()
    print("Banco de dados inicializado.")

def get_current_machine_state_from_db():
    """Obtém o estado atual da máquina, créditos e a mensagem do banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT current_state, message, credits FROM machine_state WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1], row[2] # state, message, credits
    return 'UNKNOWN', 'State not found', 0

def set_machine_state_in_db(state, message="", credits_override=None):
    """Define o estado atual da máquina e opcionalmente os créditos no banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    sql_set_parts = ["current_state = ?", "message = ?"]
    params = [state, message]

    if credits_override is not None:
        sql_set_parts.append("credits = ?")
        params.append(int(credits_override)) # Ensure credits are stored as integers

    sql = f"UPDATE machine_state SET {', '.join(sql_set_parts)} WHERE id = 1"
    cursor.execute(sql, tuple(params))
    conn.commit()
    conn.close()

    if credits_override is not None:
        credit_msg_part = f", Credits set to: {int(credits_override)}"
    else:
        credit_msg_part = " (credits unchanged)"
    print(f"Estado da máquina definido para: {state} - {message}{credit_msg_part}")

def record_punch_in_db(force_value):
    """Registra um soco no banco de dados e atualiza o estado."""
    current_state_from_db, _, _ = get_current_machine_state_from_db()

    if current_state_from_db not in ['READY_TO_PUNCH', 'PARTY_MODE_ACTIVE']:
        print(f"Soco ignorado. Estado atual: {current_state_from_db}. É necessário estar 'READY_TO_PUNCH' ou 'PARTY_MODE_ACTIVE'.")
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO score (force, timestamp) VALUES (?, ?)", (force_value, timestamp))

    new_state = 'PUNCHED'
    message = f"Soco detectado! Força: {force_value}. Exibindo resultado..."

    # Credits are not changed here; they were "spent" when transitioning to READY_TO_PUNCH
    cursor.execute("UPDATE machine_state SET current_state = ?, last_punch_time = ?, message = ? WHERE id = 1",
                   (new_state, timestamp, message))
    conn.commit()
    conn.close()
    print(f"Soco registrado no DB: Força={force_value}, Timestamp={timestamp}. Novo estado: {new_state}")

def add_credits_to_db(value_inserted):
    """
    Adds the inserted monetary value to the machine's credits in the database.
    This function ONLY updates the 'credits' field.
    It does not change the machine's state or primary message directly,
    except to prevent credit addition in PARTY_MODE_ACTIVE.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Fetch current state and credits directly to ensure atomicity for this specific operation
    cursor.execute("SELECT current_state, credits FROM machine_state WHERE id = 1")
    row = cursor.fetchone()

    if not row:
        print("Erro: Estado da máquina não encontrado em add_credits_to_db.")
        conn.close()
        return

    current_machine_state_val, current_credits_val = row

    if current_machine_state_val == 'PARTY_MODE_ACTIVE':
        print(f"Valor de R${float(value_inserted):.2f} inserido durante Modo Festa. Créditos não são alterados.")
        conn.close()
        return

    new_credits = int(current_credits_val) + int(value_inserted)

    cursor.execute("UPDATE machine_state SET credits = ? WHERE id = 1", (new_credits,))
    conn.commit()
    conn.close()
    print(f"DB: Créditos atualizados para: {new_credits}. (Valor inserido: {value_inserted})")