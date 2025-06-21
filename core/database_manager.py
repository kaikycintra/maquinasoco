import sqlite3
import time
from .config import DATABASE_NAME, GAME_COST

def _get_db_connection():
    """Cria e retorna uma conexão com o banco de dados com a factory de linhas ativada."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Inicializa o banco de dados e cria as tabelas 'score' e 'machine_state' se não existirem.
    A tabela 'score' é recriada para incluir CPF e nome, conforme esperado pelo servidor.
    A tabela 'machine_state' é inicializada com o estado 'IDLE'.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    # Apaga a tabela score antiga se existir, para garantir que o novo esquema seja aplicado.
    cursor.execute('DROP TABLE IF EXISTS score')
    
    # Tabela para armazenar pontuações com informações do jogador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            force INTEGER,
            cpf TEXT,
            nome TEXT
        )
    ''')
    
    # Tabela para o estado da máquina, contém somente uma linha
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS machine_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_state TEXT CHECK current_state IN('IDLE', 'READY_TO_PUNCH', 'PUNCHED'),
            credits INTEGER NOT NULL DEFAULT 0,
            acceleration REAL,
        )
    ''')
    
    # Garante que a linha de estado da máquina exista, inicializando-a se necessário.
    cursor.execute("INSERT INTO machine_state (id, current_state, credits) VALUES (1, 'IDLE', 0)")
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com o esquema do servidor.")

##################### OPERAÇÕES DO SERVIDOR #####################

def reset_banco():
    """
    Reinicia o banco de dados para seu estado inicial.
    Limpa todas as pontuações e redefine o estado da máquina para 'IDLE' com 0 créditos.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM score")
    cursor.execute("UPDATE machine_state SET current_state = 'IDLE', credits = 0 WHERE id=1")
    conn.commit()
    conn.close()
    print("Banco de dados reiniciado.")

def get_saldo():
    """Retorna o número de créditos (saldo) atual da máquina."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM machine_state WHERE id=1")
    row = cursor.fetchone()
    conn.close()
    return row['credits']

def get_estado_banco():
    """Retorna o estado atual da máquina ('IDLE', 'READY_TO_PUNCH' ou 'PUNCHED')."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_state FROM machine_state WHERE id=1")
    row = cursor.fetchone()
    conn.close()
    return row['current_state']

def get_leitura_acelerometro():
    """Busca a força do último soco registrado no banco de dados."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    # Assume que a leitura desejada é a do último registro na tabela score
    cursor.execute("SELECT acceleration FROM machine_state WHERE id=1")
    row = cursor.fetchone()
    conn.close()
    return row['acceleration']

def cobra_jogo():
    """
    Deduz o custo de um jogo dos créditos e atualiza o estado da máquina para 'READY_TO_PUNCH'.
    Retorna True se a cobrança for bem-sucedida, False caso contrário.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM machine_state WHERE id=1")
    row = cursor.fetchone()
    
    if not row or row['credits'] < GAME_COST:
        conn.close()
        print("Cobrança falhou: Saldo insuficiente.")
        return False
        
    new_credits = row['credits'] - GAME_COST
    cursor.execute("UPDATE machine_state SET credits = ?, current_state = 'READY_TO_PUNCH' WHERE id=1", (new_credits,))
    conn.commit()
    conn.close()
    print(f"Jogo cobrado. Novo saldo: {new_credits}. Estado: READY_TO_PUNCH")
    return True

def insere_score(cpf, nome, pontuacao):
    """
    Guarda uma nova pontuação no banco de dados com o CPF e nome do jogador.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO score (cpf, nome, force, timestamp) VALUES (?, ?, ?, ?)", (cpf, nome, pontuacao, timestamp))
    conn.commit()
    conn.close()
    print(f"Score guardado para {nome} ({cpf}): {pontuacao}")

def get_score(cpf, nome):
    """
    Busca a pontuação mais recente de um jogador específico pelo CPF e nome.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM score WHERE cpf = ? AND nome = ? ORDER BY timestamp DESC LIMIT 1", (cpf, nome))
    score = cursor.fetchone()
    conn.close()
    return score

def get_top_10():
    """
    Retorna uma lista com as 10 maiores pontuações registradas.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, force FROM score ORDER BY force DESC LIMIT 10")
    scores = cursor.fetchall()
    conn.close()
    return scores

def update_estado_idle():
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE machine_state SET current_state = 'IDLE' where id=1")
    conn.commit()
    conn.close()


##################### OPERAÇÕES DO HARDWARE #####################

def insere_credito(valor: int):
    """Adiciona créditos à máquina, somando ao saldo existente."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    # Atualiza os créditos somando o novo valor diretamente no SQL
    cursor.execute("UPDATE machine_state SET credits = credits + ? WHERE id = 1", (valor,))
    conn.commit()

    # Busca o novo saldo para exibir no log
    cursor.execute("SELECT credits FROM machine_state WHERE id = 1")
    new_credits = cursor.fetchone()['credits']
    print(f"{valor} crédito(s) inserido(s). Novo saldo: {new_credits}.")
    conn.close()

def insere_soco(cpf: str, nome: str, force: int):
    """
    Registra um soco no sistema.
    Guarda a pontuação e atualiza o estado da máquina para 'PUNCHED',
    registrando a força do soco.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO score (cpf, nome, force, timestamp) VALUES (?, ?, ?, ?)", (cpf, nome, force, timestamp))
    cursor.execute("UPDATE machine_state SET current_state = 'PUNCHED', acceleration = ? WHERE id = 1", (force,))
    conn.commit()
    print(f"Soco registrado para {nome} com força {force}. Estado da máquina: PUNCHED.")
    conn.close()
