# Maquina_soco

O sistema está dividindo em dois módulos que têm execução concorrente, o hardware e o servidor. O hardware recebe input físico de aparelhos conectados a uma raspberry pi ou de um teclado de computador. O servidor lida com o carregamento de telas.
Esses dois módulos se comunicam através do core, que configura alguns parâmetros do sistema e inicializa um banco de dados que serve para a comunicação entre o hardware e o servidor.

A ideia desse design é poder permitir que a tela mude não só com interações nela mas também com alterações no banco de dados que são feitas através de sinais de hardware. A comunicação do cliente com o servidor (toda local) é feita através de HTMX, que facilita o polling de requests para uma implementação sem websocket.