'''
Módulo responsável por converter as leituras do
acelerômetro MPU6050 em uma pontuação de 0 a 999
'''
import time

from .mpu6050 import mpu6050
from core.database_manager import insere_soco
from core.config import (
    LIMITE_INF_ACELERACAO,
    LIMITE_SUP_ACELERACAO,
    MIN_SCORE,
    MAX_SCORE,
    INTERVALO_LEITURA_SOCO)

def mapeia_valor_entre_intervalos(valor: float,
                                  lower_1: float,
                                  upper_1: float,
                                  lower_2: float,
                                  upper_2: float) -> float:
    if valor < lower_1 and valor > upper_1:
        return None
    
    # transforma valor no intervalo original para valor entre 0 e 1 (porcentagem)
    p = (valor - lower_1) / (upper_1 - lower_1)

    # transforma esse valor para dentro do segundo intervalo
    valor2 = (p) * (upper_2 - lower_2) + lower_2
    return valor2

def calcula_score(aceleracao: float) -> int:
    inf = LIMITE_INF_ACELERACAO
    sup = LIMITE_SUP_ACELERACAO
    accel = aceleracao
    min_score = MIN_SCORE
    max_score = MAX_SCORE

    # calcula score através de uma transformação linear
    score = mapeia_valor_entre_intervalos(accel, inf, sup, min_score, max_score)
    return round(score)

def maximo_no_intervalo(mpu: mpu6050) -> float:
    """
    Retorna aceleração com maior valor absoluto captado em um intervalo de tempo
    """
    inicio = time.perf_counter()
    atual = time.perf_counter()
    accel = 0.0

    while atual - inicio < INTERVALO_LEITURA_SOCO:
        accel_data = mpu.get_accel_data()
        accel = abs(accel_data['y'])

        accel = max(accel, accel_data['y'])
        atual = time.perf_counter()

    return accel

def scorecalc():
    mpu = mpu6050(0x68)

    # espera soco
    while True:
        accel_data = mpu.get_accel_data()
        accel = accel_data['y'] # |a - 0| ~ 0.1 na maior parte do tempo
        if accel > 1.0:
            break
    
    print("lendo acelerômetro...")
    accel = maximo_no_intervalo(mpu)
    print(f"aceleração detectada: {accel}")
    
    score = calcula_score(accel)
    insere_soco(score)
    return score
    