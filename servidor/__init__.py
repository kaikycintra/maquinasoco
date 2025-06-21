import time
import random

from flask import Flask, render_template, redirect, url_for, Response, request
from .utils import determina_nivel_soco
from core.config import GAME_COST
from core.database_manager import (
    reset_banco,
    get_saldo,
    get_estado_banco,
    get_leitura_acelerometro,
    get_top_10,
    insere_score,
    get_score,
    update_estado_idle,
    update_estado_press_start)

app = Flask(__name__)

def run_web_server():
    """Executa o servidor Flask."""
    print("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)

############################# TELAS #############################

@app.route('/', methods=['GET'])
def index():
    # tela mostrada ao ligar jogo
    return render_template("pages/config.html")

@app.route('/idle', methods=['GET'])
def idle():
    # tela inicial do loop de gameplay, espera saldo e start
    update_estado_idle()
    return render_template("pages/idle.html", saldo=get_saldo())

@app.route('/jogo', methods=['GET'])
def jogo():
    # tela do meio do loop de gameplay, espera soco
    return render_template("pages/jogo.html")

@app.route('/gameover', methods=['GET'])
def gameover():
    # tela final do loop de gameplay
    # se usuário grava, faz um GET para score com seu cpf e nome passados
    # se não, faz um GET para score sem argumentos no URL
    # depois de 15 segundos faz um GET para idle
    return render_template("pages/gameover.html")

############################# CONSULTAS DE HARDWARE ############################

@app.route('/saldo', methods=['GET'])
def saldo():
    # chamado repetidamente na tela idle
    saldo = get_saldo()
    estado = get_estado_banco()
    if estado == "PRESS_START" or estado == "READY_TO_PUNCH":
        return render_template("partials/saldo.html",
            saldo=saldo, liberado=False) # saldo já foi verificado, não carregar botão de novo

    liberado = saldo >= GAME_COST
    if liberado: update_estado_press_start()
    return render_template("partials/saldo.html",
        saldo=saldo, liberado=liberado)

@app.route('/checksoco')
def checksoco():
    # chamado repetidamente na tela de jogo
    estado = get_estado_banco()
    if estado == "PUNCHED":
        time.sleep(1) # delay para atualizar leitura do acelerômetro
        forca = get_leitura_acelerometro()
        nivel = determina_nivel_soco()
        return render_template("partials/animacao_soco.html", {

        })

    return Response(status=204)

#############################  OUTROS ############################

@app.route('/reset', methods=['DELETE'])
def reset():
    reset_banco()
    return render_template("partials/toast.html",
        success=True,
        message="Dados reiniciados com sucesso!")

@app.route('/score', methods=['POST'])
def score_post():
    cpf = request.form.get('cpf')
    nome = request.form.get('nome')
    pontuacao = request.form.get('pontuacao')
    if not (nome or cpf or pontuacao):
        return render_template("partials/toast.html",
            success=False,
            message="Request incompleto, falta nome, CPF ou pontuação")
    
    insere_score(cpf, nome, pontuacao) # guarda score com timestamp
    return redirect(url_for('idle'), code=302)

@app.route('/score', methods=['GET'])
def score_get():
    cpf = request.args.get('cpf')
    nome = request.args.get('nome')
    if not (cpf or nome):
        return render_template("partials/toast.html",
            success=False,
            message="Request incompleto, falta nome, CPF ou pontuação")

    scores = get_top_10()
    score_atual = get_score(cpf, nome) # score mais recente com esse cpf e nome
    # se score com cpf e nome está no top 10, destaca ela
    highlight = score_atual if score_atual in scores else None
    return render_template("partials/top10.html",
        scores=scores,
        highlight=highlight)

@app.route('/jogar', methods=['GET'])
def jogar():
    # tenta cobrar e verifica se o estado é 'READY_TO_PUNCH' ou 'INSUFFICIENT'
    estado = get_estado_banco()
    print(f"ESTADO: {estado}")
    if estado == 'INSUFFICIENT':
        update_estado_idle() # volta estado para 'IDLE', mostrando toast apenas uma vez
        return render_template("partials/toast.html",
            success=False,
            message="Saldo insuficiente")
    
    elif estado == "PRESS_START":
        return Response(status=204)
    
    elif estado == 'READY_TO_PUNCH':
        return render_template("pages/jogo.html")
    
    return render_template("partials/toast.html",
            success=False,
            message="ESTADO DO BANCO DESCONHECIDO")
