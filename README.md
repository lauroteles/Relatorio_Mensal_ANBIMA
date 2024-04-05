Automação de Relatórios Mensais para ANBIMA
Este projeto consiste em um conjunto de scripts Python desenvolvidos para automatizar a criação de relatórios mensais enviados à ANBIMA. O objetivo principal é agilizar o processo de geração desses relatórios, reduzindo o tempo necessário para compilá-los manualmente.

Funcionalidades
O projeto oferece as seguintes funcionalidades:

Processamento de Dados: Os dados necessários para os relatórios são extraídos de diversas fontes, como arquivos Excel, e processados para prepará-los para a geração do relatório.

Padronização dos Dados: Os dados são padronizados de acordo com as especificações da ANBIMA, garantindo consistência e uniformidade no relatório final.

Geração de Relatórios: Os dados processados e padronizados são utilizados para gerar o relatório final no formato CSV e Excel.

Atualização Automática de Dados: O código é projetado para ser reutilizável e permite a fácil atualização dos dados de entrada para cada mês, facilitando a geração dos relatórios mensais.

Como Usar
Configuração do Ambiente: Certifique-se de ter Python e as bibliotecas necessárias instaladas no seu ambiente. Você pode instalar as dependências listadas no arquivo requirements.txt.

Execução do Código: Execute o script principal Anbima_mensal.py passando os caminhos dos arquivos de entrada como argumentos.

Ajuste de Parâmetros: O código pode ser personalizado de acordo com as necessidades específicas do seu ambiente. Por exemplo, você pode ajustar os caminhos dos arquivos de entrada ou os parâmetros de processamento de dados.

Estrutura do Projeto
Anbima_mensal.py: Script principal que contém as classes e funções para processamento e geração de relatórios.
README.md: Este arquivo, que fornece informações sobre o projeto e instruções de uso.
requirements.txt: Arquivo de requisitos com as bibliotecas Python necessárias para executar o código.
Arquivos de Entrada: Diretório contendo os arquivos de entrada necessários para a geração dos relatórios.
Relatórios Gerados: Diretório onde os relatórios finais serão salvos após a execução do código.
Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir problemas (issues) para relatar bugs, sugerir novos recursos ou enviar solicitações de pull (pull requests) com melhorias.
