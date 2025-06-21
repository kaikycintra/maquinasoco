import threading
import time
import subprocess
from core.database_manager import init_db
from servidor import run_web_server
from hardware import hardware_signal_listener

def open_browser():
    """Waits for the server to start and then opens the browser in kiosk mode."""
    print("Aguardando o servidor web iniciar...")
    time.sleep(5)

    url = "http://localhost:5000" 
    print(f"Abrindo o navegador em {url} no modo kiosk.")
    
    try:
        subprocess.run(['chromium-browser', '--kiosk', url], check=True)
    except FileNotFoundError:
        print("ERRO: 'chromium-browser' não foi encontrado.")
        print("Por favor, instale-o com: sudo apt-get update && sudo apt-get install chromium-browser")
    except Exception as e:
        print(f"Falha ao abrir o navegador: {e}")

if __name__ == '__main__':
    init_db()

    print("Iniciando o listener de hardware em um thread de background...")
    hardware_thread = threading.Thread(target=hardware_signal_listener, daemon=True)
    hardware_thread.start()

    print("Iniciando o browser em uma thread de background...")
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    print("Iniciando o servidor na thread principal")
    run_web_server()
