# ProbSched: Simulador para Algoritmos de Escalonamento Probabilístico para Sistemas Operativos

ProbSched é um simulador de escalonamento de processos que implementa diversos algoritmos de escalonamento e utiliza distribuições probabilísticas para a geração de processos, permitindo uma análise comparativa do desempenho de cada algoritmo em diferentes cenários de carga.

## 📋 Descrição

O ProbSched foi desenvolvido como parte de um projeto acadêmico para modelar o comportamento de diferentes algoritmos de escalonamento em sistemas operativos. O simulador permite a comparação objetiva entre diferentes estratégias de escalonamento e a análise do seu desempenho sob diversas condições de carga.

## ✨ Funcionalidades

- Implementação de múltiplos algoritmos de escalonamento:
  - First-Come First-Served (FCFS)
  - Shortest Job First (SJF) - versão não preemptiva
  - Shortest Job First (SJF) - versão preemptiva (SRTF)
  - Round Robin (RR)
- Geração de processos utilizando distribuições probabilísticas:
  - Tempos de chegada gerados via distribuição de Poisson
  - Tempos de execução gerados via distribuição exponencial ou normal
  - Prioridades geradas via distribuição uniforme ou ponderada
- Métricas de desempenho detalhadas:
  - Tempo médio de espera
  - Tempo médio de resposta total
  - Taxa de processamento
  - Utilização da CPU
- Visualização gráfica dos resultados
- Configuração flexível via linha de comandos ou arquivo JSON

## 🔧 Requisitos do Sistema

- Python 3.6 ou superior
- Bibliotecas: NumPy, Matplotlib

## 📥 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/ti-almeida/probsched.git
cd probsched
```

2. Instale as dependências:
```bash
pip install numpy matplotlib
```

## 🚀 Uso

### Via linha de comandos:

```bash
python TrabalhoSO.py --num-processos 25 --taxa-chegada 0.8 --distribuicao-execucao exponential --algoritmos FCFS SJF-NP SJF-P RR --quantum-tempo 4
```

### Via arquivo de configuração:

1. Crie um arquivo `config.json`:
```json
{
    "num_processos": 25,
    "taxa_chegada": 0.8,
    "distribuicao_execucao": "exponential",
    "algoritmos": ["FCFS", "SJF-NP", "SJF-P", "RR"],
    "quantum_tempo": 4,
    "sem_visualizacao": false
}
```

2. Execute o simulador:
```bash
python TrabalhoSO.py --config config.json
```

## 📊 Resultados

Os resultados da execução do simulador mostram diferenças significativas no desempenho dos algoritmos:

| **Algoritmo** | **Tempo Médio de Espera** | **Tempo Médio de Resposta** | **Taxa de Processamento** | **Utilização da CPU (%)** |
|---------------|---------------------------|----------------------------|--------------------------|--------------------------|
| FCFS          | 95.65                     | 104.27                     | 0.12                     | 99.54                    |
| SJF (Não Preemptivo) | 40.65               | 49.27                      | 0.12                     | 99.73                    |
| SJF (Preemptivo) | 43.15                  | 52.07                      | 0.11                     | 94.69                    |
| Round Robin (Q=4) | 76.57                 | 87.41                      | 0.12                     | 99.54                    |

## 🧪 Distribuições Probabilísticas

O simulador utiliza as seguintes distribuições para geração de processos:

- **Tempos de Chegada**: Distribuição de Poisson
- **Tempos de Execução**: Distribuição Exponencial ou Normal
- **Prioridades**: Distribuição Uniforme ou Ponderada (Beta)

## 🏗️ Estrutura do Projeto

```
ProbSched/
├── TrabalhoSO.py    # Código principal do simulador
├── config.json      # Arquivo de configuração
├── makefile         # MakeFile
└── README.md        # Documentação
```

## 🤝 Contribuidores

- Alvaro Frias Nº49400
- Eduardo Mesquita Nº49507
- João Mariz Nº48154
- Tiago Almeida Nº48278

## 📚 Referências

1. [NumPy Documentation](https://numpy.org/doc/)
2. [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
