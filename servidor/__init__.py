from flask import Flask, render_template, jsonify, redirect, url_for, session, make_response
from core.database_manager import (
    get_current_machine_state_from_db,
    set_machine_state_in_db,
    init_db as initialize_database, # Renomeado para evitar conflito com rota
    DATABASE_NAME, # Para a função de reset
    GAME_COST
)
import sqlite3 # Para resetar
import os # Para secret_key

app = Flask(__name__)
app.secret_key = os.urandom(24) # Necessário para sessões

STATE_DISPLAY_NAMES = {
    "IDLE": "Disponível",
    "WAITING_FOR_COIN": "Aguardando Moeda",
    "READY_TO_PUNCH": "Pronto para Socar!",
    "PARTY_MODE_ACTIVE": "Modo Festa Ativo (Soco Grátis!)",
    "PUNCHED": "Soco Detectado! Processando..."
}

def run_web_server():
    """Executa o servidor Flask."""
    print("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000, debug=False)

@app.route('/')
def index():
    session.pop('in_play_mode', None) # Limpa o estado de jogo ao voltar para o menu principal
    current_state_code, current_message, current_credits = get_current_machine_state_from_db()
    return render_template('index.html',
                           # Para o conteúdo inicial que o HTMX irá substituir
                           initial_status_text=STATE_DISPLAY_NAMES.get(current_state_code, current_state_code),
                           initial_message_text=current_message, # Mensagem já inclui créditos
                           initial_credits=current_credits) # Pode ser usado no template se necessário

@app.route('/select_mode/<mode_name>')
def select_mode(mode_name):
    current_db_state, _, current_credits = get_current_machine_state_from_db() # Get current state and credits
    current_credits_int = int(current_credits)

    if mode_name == 'play':
        session['in_play_mode'] = True # Mark that a game play sequence is starting
        if current_db_state == 'PARTY_MODE_ACTIVE':
            # Machine is already in party mode, "Play" click confirms starting a round.
            # State remains PARTY_MODE_ACTIVE, message can be updated for play screen.
            # Credits are preserved as set_machine_state_in_db no longer auto-resets them for PARTY_MODE_ACTIVE.
            set_machine_state_in_db('PARTY_MODE_ACTIVE', 'Modo Festa! Pronto para o soco!')
        else:
            # Standard play: check credits and proceed.
            if current_credits_int >= GAME_COST:
                new_credits = current_credits_int - GAME_COST
                message_ready = f'Crédito: R${float(new_credits):.2f}. Pronto para o soco!'
                set_machine_state_in_db('READY_TO_PUNCH', message_ready, credits_override=new_credits)
            else:
                needed = GAME_COST - current_credits_int
                message_wait = f'Crédito: R${float(current_credits_int):.2f}. Faltam R${float(needed):.2f} para jogar.'
                set_machine_state_in_db('WAITING_FOR_COIN', message_wait, credits_override=current_credits_int)
        return redirect(url_for('play_game_screen'))

    elif mode_name == 'party':
        session.pop('in_play_mode', None) # Clear any previous game play session
        # Set the machine state to party mode. Credits are preserved.
        set_machine_state_in_db('PARTY_MODE_ACTIVE', 'Modo Festa Ativado! Clique em "Jogar" para iniciar uma rodada.')
        return redirect(url_for('index')) # Go back to index, status will update via HTMX

    elif mode_name == 'reset':
        session.pop('in_play_mode', None)
        # CUIDADO: Isto apaga todos os scores!
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM score")
            conn.commit()
        finally:
            if conn:
                conn.close()
        # Explicitly reset credits to 0 for a full reset.
        set_machine_state_in_db('IDLE', 'Todos os dados de score foram resetados. Máquina em modo IDLE.', credits_override=0)
        return render_template('message_page.html', title="Dados Resetados", message="Todos os scores foram apagados e a máquina está em modo IDLE.")
    return redirect(url_for('index')) # Default redirect if mode_name is unknown

@app.route('/play_game')
def play_game_screen():
    current_state_code, current_message, current_credits = get_current_machine_state_from_db()
    # Se o estado já for IDLE ao entrar aqui (ex: refresh após fim de jogo), limpar flag
    if current_state_code == 'IDLE' and session.get('in_play_mode'):
        session.pop('in_play_mode', None)
        # Poderia redirecionar para o index aqui também, ou deixar o HTMX polling tratar
        # IDLE state will have 0 credits due to set_machine_state_in_db logic

    return render_template('play_screen.html',
                           # Para o conteúdo inicial que o HTMX irá substituir
                           initial_status_text=STATE_DISPLAY_NAMES.get(current_state_code, current_state_code),
                           initial_message_text=current_message, # Mensagem já inclui créditos
                           initial_credits=current_credits)

@app.route('/htmx/status_fragment')
def htmx_status_fragment():
    state_code, message, credits = get_current_machine_state_from_db() # Credits available if needed by template
    display_name = STATE_DISPLAY_NAMES.get(state_code, state_code)

    response_html = render_template('_status_fragment.html',
                                    status_text=display_name,
                                    message_text=message,
                                    credits=credits) # Passa os créditos para o fragmento
    response = make_response(response_html)

    if session.get('in_play_mode') and state_code == 'IDLE':
        session.pop('in_play_mode', None)
        response.headers['HX-Redirect'] = url_for('index')
    return response
