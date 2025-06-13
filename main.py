import threading
import time
from core.database_manager import init_db
from servidor.server import run_web_server
from hardware import hardware_signal_listener

if __name__ == '__main__':
    init_db()

    web_server_thread = threading.Thread(target=run_web_server, daemon=True)
    hardware_thread = threading.Thread(target=hardware_signal_listener, daemon=True)

    web_server_thread.start()
    hardware_thread.start()

    print("Aplicação principal iniciada. Pressione Ctrl+C para sair.")
    try:
        while True:
            # Mantém a thread principal viva.
            # O listener de hardware mock (input()) bloqueará esta thread se não estiver em daemon.
            # Se o listener de hardware for daemon, este loop é necessário para manter o programa rodando.
            # Se o listener de hardware não for daemon e usar input(), este loop pode não ser estritamente
            # necessário para manter o programa vivo, mas é uma boa prática para o encerramento gracioso.
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\nEncerrando aplicação...")
    finally:
        print("Threads finalizadas.")
        # Nota: Threads daemon são encerradas abruptamente quando a thread principal termina.
        # Para um encerramento mais gracioso de threads daemon, você pode implementar
        # mecanismos de sinalização (como Events) para que elas terminem seu trabalho.
        # No caso do listener GPIO, o GPIO.cleanup() já está no finally dele.
        # O servidor Flask em modo debug=False também deve encerrar relativamente bem.