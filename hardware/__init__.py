from .mock_listener import start_keyboard_mock_listener

def hardware_signal_listener():
    """
    Inicia o listener de sinais de hardware
    Pode ser incrementado para diferentes opções de listeners
    """
    start_keyboard_mock_listener()