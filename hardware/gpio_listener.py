import time
from core.database_manager import record_punch_in_db, add_credits_to_db, get_current_machine_state_from_db
from core.config import SENSOR_PIN, MONEY_SENSOR_PIN, GAME_COST
import RPi.GPIO as GPIO

def start_gpio_listener():
    """Escuta sinais de hardware GPIO no Raspberry Pi ou simula com MockGPIO."""
    print("Iniciando listener de hardware GPIO...")
    GPIO.setmode(GPIO.BCM)
    # Configuração do sensor de soco
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Configuração do sensor de moeda
    GPIO.setup(MONEY_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def punch_signal_callback(channel):
        print(f"Sinal de hardware recebido no pino {channel} (soco)!")
        current_state, _, _ = get_current_machine_state_from_db()
        if current_state == 'READY_TO_PUNCH' or current_state == 'PARTY_MODE_ACTIVE':
            simulated_force = 75.5  # Substitua pela leitura real do sensor
            record_punch_in_db(simulated_force)
        else:
            print(f"Sinal de soco ignorado no pino {channel}. Estado atual: {current_state}")

    def money_signal_callback(channel):
        print(f"Sinal de moeda recebido no pino {channel}!")
        add_credits_to_db(GAME_COST) # Usa GAME_COST para o valor do crédito

    GPIO.add_event_detect(SENSOR_PIN, GPIO.FALLING, callback=punch_signal_callback, bouncetime=300)
    GPIO.add_event_detect(MONEY_SENSOR_PIN, GPIO.FALLING, callback=money_signal_callback, bouncetime=300)
    print(f"Listeners de hardware GPIO configurados: Soco no pino {SENSOR_PIN}, Moeda no pino {MONEY_SENSOR_PIN}.")

    try:
        while True:
            time.sleep(1)  # Mantenha a thread viva para os callbacks GPIO
    except KeyboardInterrupt:
        print("\nListener de hardware (GPIO) interrompido.")
    except Exception as e:
        print(f"Erro no listener GPIO: {e}")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    # Este bloco é para teste direto do gpio_listener.py
    # Certifique-se de que database_manager e config são acessíveis.
    print("Testando gpio_listener diretamente...")
    # Mockup simples para dependências se não estiverem configuradas para teste direto
    def _mock_db_call(val): print(f"Mock DB call with: {val}")
    def _mock_get_state(): return 'READY_TO_PUNCH', 0, 0
    global record_punch_in_db, add_credits_to_db, get_current_machine_state_from_db
    record_punch_in_db = _mock_db_call
    add_credits_to_db = _mock_db_call
    get_current_machine_state_from_db = _mock_get_state
    
    # Mockup para config se não estiverem configuradas
    global SENSOR_PIN, MONEY_SENSOR_PIN, GAME_COST
    SENSOR_PIN = 17 # Exemplo
    MONEY_SENSOR_PIN = 18 # Exemplo
    GAME_COST = 1 # Exemplo
    
    start_gpio_listener()
