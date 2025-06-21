from core.database_manager import insere_score, insere_credito, get_estado_banco
from pynput import keyboard

def start_keyboard_mock_listener():
    """Simula sinais de hardware com entrada de teclado."""
    # Pynput listener logic
    print("\nModo Mock (pynput):")
    print("  ESPAÇO: Simular soco")
    print("  '2': Inserir R$2.00")
    print("  '5': Inserir R$5.00 (ou 'c')")
    print("  'q': Inserir R$20.00")
    print("  'w': Inserir R$50.00")
    print("  'e': Inserir R$100.00")
    print("  'r': Inserir R$200.00")
    print("  ESC: Sair do listener")

    def on_press(key):
        try:
            if key == keyboard.Key.space:
                current_state, _, _ = get_estado_banco()
                if current_state == 'READY_TO_PUNCH':
                    simulated_force = 50.0
                    print("Simulando soco (ESPAÇO pressionado)...")
                    insere_score("12131415678", "kaiky", simulated_force)
                else:
                    print(f"Simulação de soco ignorada. Estado: {current_state}")
            elif hasattr(key, 'char'):
                char = key.char
                if char == '2': insere_credito(2); print("Créditos (R$2) adicionados.")
                elif char == '5' or char == 'c': insere_credito(5); print("Créditos (R$5) adicionados.")
                elif char == 'q': insere_credito(20); print("Créditos (R$20) adicionados.")
                elif char == 'w': insere_credito(50); print("Créditos (R$50) adicionados.")
                elif char == 'e': insere_credito(100); print("Créditos (R$100) adicionados.")
                elif char == 'r': insere_credito(200); print("Créditos (R$200) adicionados.")
        except Exception as e:
            print(f"Erro ao processar tecla: {e}")

    def on_release(key):
        if key == keyboard.Key.esc:
            print("Tecla ESC pressionada, parando o listener de mock (pynput)...")
            return False  # Stops the listener

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    print("Listener de mock (pynput) iniciado. Pressione ESC para sair.")

    try:
        listener.join()  # Block until the listener stops
    except KeyboardInterrupt:
        print("\nListener de mock (pynput) interrompido via Ctrl+C.")
        if listener.running:
            listener.stop()
    finally:
        print("Listener de mock (pynput) finalizado.")
