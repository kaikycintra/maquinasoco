from core.database_manager import insere_soco, insere_credito, get_estado_banco, cobra_jogo
from pynput import keyboard

def start_keyboard_mock_listener():
    """Simula sinais de hardware com entrada de teclado."""
    print("\nModo Mock (pynput) - Teclas de Simulação:")
    print("  '1', '2', '3': Simular soco (forças 30, 50, 90)")
    print("  '7': Inserir R$2.00")
    print("  '8': Inserir R$5.00")
    print("  '9': Inserir R$20.00")
    print("  '5': Aperta START")
    print("  ESC: Sair do listener")

    def on_press(key):
        try:
            if not hasattr(key, 'char'):
                return

            char = key.char
            if char in ['1', '2', '3']:
                current_state = get_estado_banco()
                if current_state == 'READY_TO_PUNCH':
                    force = '30' if char == '1' else ('50' if char == '2' else '90')
                    print(f"Simulando soco (tecla '{char}' pressionada)...")
                    insere_soco(force)
                else:
                    print(f"Simulação de soco ignorada. Estado: {current_state}")

            elif char in ['7', '8', '9']:
                valor = 2 if char == '7' else (5 if char == '8' else 20)
                insere_credito(valor)
                print(f"Créditos (R${valor}) adicionados.")

            elif char in ['5']:
                cobra_jogo()
                print("Botão START apertado.")

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
