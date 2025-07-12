# 🥊 Maquina\_soco

Este projeto é um sistema de jogo interativo que combina hardware e software para criar uma experiência reativa, como uma máquina de soco.

## Arquitetura do Sistema

O sistema está dividido em dois módulos principais que executam de forma concorrente:

  * **Módulo Hardware:** Responsável por capturar inputs físicos, seja de periféricos conectados a uma **Raspberry Pi** (como um acelerômetro) ou de um teclado de computador para fins de teste.

  * **Módulo Servidor:** Gerencia a interface do usuário e o carregamento das telas, respondendo a interações.

Esses dois módulos não se comunicam diretamente. Em vez disso, eles interagem através de um **módulo Core**, que inicializa um banco de dados compartilhado. O hardware escreve os sinais dos sensores no banco de dados, e o servidor lê essas alterações para atualizar a tela dinamicamente.

Este design permite que a interface mude não apenas com cliques, mas também em resposta a eventos físicos. A comunicação do cliente com o servidor é feita com **HTMX**, que facilita o polling de requisições para uma implementação reativa sem a necessidade de WebSockets.

## ⚙️ Instalação e Configuração

### Pré-requisitos

  * **Hardware:**
      * Raspberry Pi
      * Acelerômetro MPU-6050
  * **Software:**
      * Python 3.x

### Passos de Instalação

1.  **Crie e ative um ambiente virtual:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Conecte e configure o acelerômetro:**
    Conecte o seu acelerômetro MPU-6050 na Raspberry Pi e siga as instruções de configuração de I2C detalhadas no [repositório do mpu6050](https://github.com/m-rtijn/mpu6050/blob/master/README.rst).

## ▶️ Executando

Altere a constante em core/config.py, por padrão RASPBERRY é False (para teste em qualquer computador). Para rodar em uma RASPBERRY é necessário alterá-la para True.

### Aplicação Principal

Para rodar o jogo, execute o script principal:

```bash
python main.py
```

### Teste do Acelerômetro

Para verificar se a conexão com o MPU-6050 está funcionando corretamente, você pode rodar o script de hardware de forma isolada:

```bash
python hardware/mpu6050.py
```