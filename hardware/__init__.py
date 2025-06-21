# Este módulo agora atua como um dispatcher para o listener de hardware apropriado.
#try:
#    import RPi.GPIO # Usado apenas para detectar a disponibilidade do Raspberry Pi
#    RASPBERRY_PI_AVAILABLE = True
#except ImportError:
RASPBERRY_PI_AVAILABLE = False

def hardware_signal_listener():
    """
    Inicia o listener de sinais de hardware apropriado.
    Usa RPi.GPIO se disponível (em um Raspberry Pi), caso contrário, usa um mock de teclado.
    """
    if RASPBERRY_PI_AVAILABLE:
        print("Raspberry Pi detectado (ou RPi.GPIO disponível). Iniciando listener GPIO.")
        # Usando import relativo assumindo que os arquivos estão no mesmo pacote/diretório.
        from .gpio_listener import start_gpio_listener
        start_gpio_listener()
    else:
        print("Raspberry Pi não detectado ou RPi.GPIO indisponível. Iniciando listener de mock de teclado.")
        from .mock_listener import start_keyboard_mock_listener
        start_keyboard_mock_listener()

# Para teste direto do listener (opcional)
if __name__ == '__main__':
    # Se executado diretamente, pode ser necessário ajustar o sys.path para imports relativos
    # ou executar como um módulo, ex: python -m servidor.hardware_listener
    print("Iniciando hardware_signal_listener a partir de __main__...")
    hardware_signal_listener()
