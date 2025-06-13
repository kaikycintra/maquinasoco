from core.database_manager import record_punch_in_db, add_credits_to_db, get_current_machine_state_from_db
# GAME_COST from config is not directly used here as mock uses hardcoded values.

PYNPUT_AVAILABLE = False
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    print("pynput não encontrado. O mock de teclado usará input() como fallback.")

def start_keyboard_mock_listener():
    """Simula sinais de hardware com entrada de teclado (pynput ou input() fallback)."""

    if not PYNPUT_AVAILABLE:
        print("\nUsando input() como fallback para simulação de eventos:")
        print("  'soco': Simular soco")
        print("  '2': Inserir R$2.00")
        print("  '5' ou 'c': Inserir R$5.00")
        print("  'q': Inserir R$20.00")
        print("  'w': Inserir R$50.00")
        print("  'e': Inserir R$100.00")
        print("  'r': Inserir R$200.00")
        print("  'exit': Sair do listener")
        while True:
            try:
                cmd = input("Mock input> ").strip().lower()
                if cmd == 'soco':
                    current_state, _, _ = get_current_machine_state_from_db()
                    if current_state == 'READY_TO_PUNCH' or current_state == 'PARTY_MODE_ACTIVE':
                        simulated_force = 50.0
                        print("Simulando soco...")
                        record_punch_in_db(simulated_force)
                    else:
                        print(f"Simulação de soco ignorada. Estado: {current_state}")
                elif cmd == '2': add_credits_to_db(2); print("Créditos (R$2) adicionados.")
                elif cmd == '5' or cmd == 'c': add_credits_to_db(5); print("Créditos (R$5) adicionados.")
                elif cmd == 'q': add_credits_to_db(20); print("Créditos (R$20) adicionados.")
                elif cmd == 'w': add_credits_to_db(50); print("Créditos (R$50) adicionados.")
                elif cmd == 'e': add_credits_to_db(100); print("Créditos (R$100) adicionados.")
                elif cmd == 'r': add_credits_to_db(200); print("Créditos (R$200) adicionados.")
                elif cmd == 'exit':
                    print("Saindo do listener de input().")
                    break
                else:
                    print(f"Comando desconhecido: {cmd}")
            except KeyboardInterrupt:
                print("\nListener de input() interrompido.")
                break
            except EOFError:
                print("\nListener de input() interrompido (EOF).")
                break
            except Exception as e:
                print(f"Erro no listener de input(): {e}")
        return

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
                current_state, _, _ = get_current_machine_state_from_db()
                if current_state == 'READY_TO_PUNCH' or current_state == 'PARTY_MODE_ACTIVE':
                    simulated_force = 50.0
                    print("Simulando soco (ESPAÇO pressionado)...")
                    record_punch_in_db(simulated_force)
                else:
                    print(f"Simulação de soco ignorada. Estado: {current_state}")
            elif hasattr(key, 'char'):
                char = key.char
                if char == '2': add_credits_to_db(2); print("Créditos (R$2) adicionados.")
                elif char == '5' or char == 'c': add_credits_to_db(5); print("Créditos (R$5) adicionados.")
                elif char == 'q': add_credits_to_db(20); print("Créditos (R$20) adicionados.")
                elif char == 'w': add_credits_to_db(50); print("Créditos (R$50) adicionados.")
                elif char == 'e': add_credits_to_db(100); print("Créditos (R$100) adicionados.")
                elif char == 'r': add_credits_to_db(200); print("Créditos (R$200) adicionados.")
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

if __name__ == '__main__':
    # Este bloco é para teste direto do keyboard_mock_listener.py
    print("Testando keyboard_mock_listener diretamente...")
    # Mockup simples para dependências
    def _mock_db_call(val): print(f"Mock DB call with: {val}")
    def _mock_get_state(): return 'READY_TO_PUNCH', 0, 0
    global record_punch_in_db, add_credits_to_db, get_current_machine_state_from_db
    record_punch_in_db = _mock_db_call
    add_credits_to_db = _mock_db_call
    get_current_machine_state_from_db = _mock_get_state
    
    start_keyboard_mock_listener()
