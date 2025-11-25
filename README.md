# programa-o-p-e-d# Simulador Paralelo e Distribuído de Escalonamento de Processos

Um simulador completo de escalonamento de processos desenvolvido em Python com interface web usando Streamlit. Permite testar e comparar diferentes algoritmos de escalonamento (FCFS, SJF, Round Robin e Prioridade Preemptiva).

## Objetivo

Este projeto implementa um módulo de simulação de escalonamento de processos que:

- Recebe e armazena processos de múltiplas fontes
- Oferece a escolha de diferentes algoritmos de escalonamento
- Executa simulações com threads
- Calcula e exibe métricas de desempenho
- Permite comparação entre algoritmos

## Começando

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone ou baixe o projeto

```bash
git clone <url-do-repositorio>
cd simulador-escalonamento
```

2. Instale as dependências

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install streamlit pandas matplotlib
```

3. Execute o aplicativo

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em http://localhost:8501

## Como Usar

### 1. Adicionar Processos (Aba: Entrada de Processos)

#### Opção A: Adicionar Manualmente

- Preencha os campos:
  - Process ID: Identificador único do processo (ex: P1, P2)
  - Arrival Time: Tempo em que o processo chega na fila (unidades de tempo)
  - CPU Duration: Quanto tempo o processo precisa de CPU (burst)
  - Priority: Prioridade do processo (números menores = prioridade maior)
- Clique em "Add Process"
- Repita para adicionar mais processos

#### Opção B: Importar de Arquivo CSV

- Prepare um arquivo CSV com os seguintes campos:

```
id,tempoChegada,duracaoCPU,prioridade
P1,0,8,0
P2,1,4,1
P3,2,2,2
```

- Clique em "Upload CSV file" e selecione o arquivo
- Os processos serão importados automaticamente

### 2. Executar Simulação (Aba: Simulação)

- Selecione o Algoritmo:

  - FCFS: First Come, First Served (quem chega primeiro executa primeiro)
  - SJF: Shortest Job First (executa o processo com menor duração)
  - Round Robin: Processa com quantum de tempo (ideal para multitarefa)
  - Prioridade Preemptiva: Executa por ordem de prioridade

- Configure o Quantum (se usar Round Robin):

  - Defina quantas unidades de tempo cada processo pode usar por vez
  - Padrão: 2 unidades

- Clique em "Run Simulation"
- Aguarde até a simulação ser concluída

### 3. Visualizar Resultados (Aba: Resultados)

Após rodar a simulação, você verá:

- Métricas Principais (em cards):

  - Avg Wait Time: Tempo médio de espera de todos os processos
  - Avg Return Time: Tempo médio do processo desde a chegada até o término
  - Avg Response Time: Tempo médio até o primeiro acesso à CPU
  - Real Time: Tempo real de execução da simulação

- Tabela de Métricas por Processo:

  - ID do processo
  - Tempo de chegada
  - Duração na CPU
  - Prioridade
  - Tempo de espera
  - Tempo de retorno
  - Tempo de resposta

- Diagrama de Gantt:
  - Visualização gráfica da linha do tempo de execução
  - Cada barra representa um processo sendo executado

### 4. Comparar Algoritmos (Aba: Comparação)

Execute pelo menos 2 algoritmos diferentes e compare:

- Tabela Comparativa: Exibe todas as métricas lado a lado
- Gráficos de Comparação:
  - Gráfico de barras com tempos médios
  - Gráfico de tempo real de execução

## Estrutura do Projeto

```
simulador-escalonamento/
│
├── app.py                 # Aplicativo principal com Streamlit
├── requirements.txt       # Dependências do projeto
├── README.md             # Este arquivo
│
└── exemplos/
    └── processos_exemplo.csv  # Arquivo de exemplo de processos
```

## Componentes Principais

### Modelo de Processo (Processo)

Representa um processo com atributos:

- id: Identificador único
- tempoChegada: Quando o processo chega
- duracaoCPU: Quanto tempo precisa de CPU
- prioridade: Nível de prioridade
- tempoEspera: Calculado após simulação
- tempoRetorno: Calculado após simulação
- tempoResposta: Calculado após simulação

### Algoritmos de Escalonamento

#### FCFS (First Come, First Served)

- Executa processos na ordem de chegada
- Simples, mas pode ter maior tempo de espera
- Ideal para processos homogêneos

#### SJF (Shortest Job First)

- Executa o processo com menor duração primeiro
- Minimiza tempo médio de espera
- Pode sofrer de starvation

#### Round Robin

- Cada processo executa por um tempo (quantum)
- Implementação de justiça no acesso à CPU
- Quantum configurável

#### Prioridade Preemptiva

- Executa por ordem de prioridade
- Números menores = prioridade maior
- Pode sofrer de starvation sem aging

### Métricas Calculadas

- Tempo de Espera: inicioExecução - tempoChegada
- Tempo de Retorno: fimExecução - tempoChegada
- Tempo de Resposta: primeiroInicioExecução - tempoChegada

## Exemplos de Uso

### Exemplo 1: Simular FCFS com 4 Processos

Arquivo processos.csv:

```
id,tempoChegada,duracaoCPU,prioridade
P1,0,8,0
P2,1,4,1
P3,2,2,2
P4,3,1,3
```

1. Importe o arquivo
2. Selecione FCFS
3. Clique em "Run Simulation"
4. Veja o resultado e o Gantt chart

### Exemplo 2: Comparar Todos os Algoritmos

1. Importe os mesmos processos
2. Execute FCFS e veja os resultados
3. Execute SJF e veja os resultados
4. Execute Round Robin (quantum=2) e veja os resultados
5. Execute Prioridade Preemptiva e veja os resultados
6. Vá à aba "Comparison" para comparar todos

## Interpretando os Resultados

### Gantt Chart

- Cada barra colorida representa um processo
- O eixo X mostra o tempo
- Você pode ver a ordem de execução e os períodos ociosos da CPU

### Métricas

- Tempo de Espera Baixo: Processo não ficou muito tempo aguardando
- Tempo de Retorno Baixo: Processo foi concluído rapidamente
- Tempo de Resposta: Importante para sistemas interativos

### Comparação

- Compare qual algoritmo tem o melhor tempo médio de espera
- Veja qual é mais eficiente em termos de tempo real

## Configurações Disponíveis

### Quantum (Round Robin)

- Valor padrão: 2 unidades de tempo
- Valores menores = mais context switches
- Valores maiores = menos context switches

### Prioridade

- Número inteiro (0, 1, 2, ...)
- 0 = maior prioridade
- Números maiores = menor prioridade

## Troubleshooting

### ModuleNotFoundError: No module named 'streamlit'

```bash
pip install streamlit
```

### Gráficos não aparecem

- Verifique se matplotlib está instalado
- pip install matplotlib

### Simulação muito lenta

- Reduza o número de processos
- Verifique se a duração dos processos não é muito alta

## Recursos Opcionais Implementados

- Visualização em Gantt Chart
- Comparação de múltiplos algoritmos
- Importação de CSV
- Interface web intuitiva
- Métricas detalhadas por processo

## Conceitos Teóricos

### FCFS (Não Preemptivo)

Ordem: 1º a chegar - 1º a executar
Vantagem: Implementação simples
Desvantagem: Tempo de espera pode ser alto

### SJF (Não Preemptivo)

Ordem: Processo com menor duração - Executar primeiro
Vantagem: Minimiza tempo médio de espera
Desvantagem: Conhecer duração antecipadamente; starvation

### Round Robin

Ordem: Cada processo tem quantum de tempo
Vantagem: Justiça, bom para sistemas interativos
Desvantagem: Mais context switches

### Prioridade Preemptiva

Ordem: Por prioridade
Vantagem: Processos importantes executam primeiro
Desvantagem: Starvation de processos de baixa prioridade

## Arquivos de Exemplo

### processos_exemplo.csv

```csv
id,tempoChegada,duracaoCPU,prioridade
P1,0,3,2
P2,1,6,1
P3,2,3,2
P4,3,5,0
P5,4,2,1
```

## Suporte

Para problemas ou dúvidas:

1. Verifique se todas as dependências estão instaladas
2. Verifique o formato do CSV
3. Teste com um número reduzido de processos

## Licença

Este projeto é fornecido como material educacional.

## Autor

Simulador de Escalonamento de Processos - 2024

---

Dica: Sempre teste com números pequenos primeiro para entender como cada algoritmo funciona antes de rodar simulações maiores!
