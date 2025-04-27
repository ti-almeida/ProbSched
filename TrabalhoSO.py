class Processo:
    def __init__(self, pid, tempo_chegada, tempo_execucao, prioridade=None, periodo=None):
        """
        Inicializa um processo com atributos chave
        
        :param pid: Identificador do Processo
        :param tempo_chegada: Tempo em que o processo chega
        :param tempo_execucao: Tempo de execução na CPU para o processo
        :param prioridade: Prioridade do processo (opcional)
        :param periodo: Período para processos em tempo real (opcional)
        """
        self.pid = pid
        self.tempo_chegada = tempo_chegada
        self.tempo_execucao = tempo_execucao
        self.tempo_execucao_original = tempo_execucao
        self.prioridade = prioridade
        self.periodo = periodo
        
        # Métricas de acompanhamento
        self.tempo_espera = 0
        self.tempo_resposta_total = 0
        self.tempo_conclusao = None
        self.tempo_resposta = None
        
    def __repr__(self):
        return f"Processo(pid={self.pid}, chegada={self.tempo_chegada}, execucao={self.tempo_execucao}, prioridade={self.prioridade})"
    
import numpy as np
import random

class GeradorProcessos:
    @staticmethod
    def gerar_chegadas_poisson(taxa, num_processos, tempo_inicial=0):
        """
        Gera tempos de chegada usando a distribuição de Poisson
        
        :param taxa: Número médio de chegadas por unidade de tempo
        :param num_processos: Número de processos a gerar
        :param tempo_inicial: Tempo inicial para o primeiro processo
        :return: Lista de tempos de chegada
        """
        tempos_entre_chegadas = np.random.exponential(1/taxa, num_processos)
        tempos_chegada = tempo_inicial + np.cumsum(tempos_entre_chegadas)
        return tempos_chegada.tolist()
    
    @staticmethod
    def gerar_tempos_execucao(distribuicao='exponential', num_processos=10, media=10, desvio_padrao=3):
        """
        Gera tempos de execução na CPU usando a distribuição especificada
        
        :param distribuicao: 'exponential' ou 'normal'
        :param num_processos: Número de processos
        :param media: Tempo médio de execução
        :param desvio_padrao: Desvio padrão
        :return: Lista de tempos de execução
        """
        if distribuicao == 'exponential':
            return np.random.exponential(media, num_processos).tolist()
        elif distribuicao == 'normal':
            return np.abs(np.random.normal(media, desvio_padrao, num_processos)).tolist()
    
    @staticmethod
    def gerar_prioridades(num_processos, distribuicao='uniform', prioridade_min=1, prioridade_max=10):
        """
        Gera prioridades dos processos
        
        :param num_processos: Número de processos
        :param distribuicao: 'uniform' ou 'weighted'
        :param prioridade_min: Valor mínimo de prioridade
        :param prioridade_max: Valor máximo de prioridade
        :return: Lista de prioridades
        """
        if distribuicao == 'uniform':
            return [random.randint(prioridade_min, prioridade_max) 
                    for _ in range(num_processos)]
        elif distribuicao == 'weighted':
            # Mais provável ter números de prioridade baixa
            return [int(np.random.beta(2, 5) * (prioridade_max - prioridade_min) + prioridade_min) 
                    for _ in range(num_processos)]
        
class EscalonadorBase:
    def __init__(self, processos):
        """
        Inicializa o escalonador com uma lista de processos
        
        :param processos: Lista de objetos do tipo Processo
        """
        self.processos_originais = sorted(processos, key=lambda p: p.tempo_chegada)
        self.processos = self.processos_originais.copy()
        self.tempo_atual = 0
        self.processos_concluidos = []
        
    def calcular_metricas(self):
        """
        Calcula métricas gerais de escalonamento
        """
        if not self.processos_concluidos:
            return None
        
        tempos_espera = [p.tempo_espera for p in self.processos_concluidos]
        tempos_resposta_total = [p.tempo_resposta_total for p in self.processos_concluidos]
        
        return {
            'tempo_espera_medio': np.mean(tempos_espera),
            'tempo_resposta_total_medio': np.mean(tempos_resposta_total),
            'taxa_processamento': len(self.processos_concluidos) / self.tempo_atual if self.tempo_atual > 0 else 0,
            'utilizacao_cpu': sum(p.tempo_execucao_original for p in self.processos_concluidos) / max(self.tempo_atual, 1) * 100
        }
    
    def executar(self):
        """
        A implementar pelos algoritmos de escalonamento específicos
        """
        raise NotImplementedError("As subclasses devem implementar o método executar")
    

class EscalonadorFCFS(EscalonadorBase):
    def executar(self):
        """
        First-Come, First-Served Scheduling
        """
        fila_prontos = []
        while self.processos or fila_prontos:
            # Adiciona processos recém-chegados à fila de prontos
            recem_chegados = [p for p in self.processos if p.tempo_chegada <= self.tempo_atual]
            fila_prontos.extend(recem_chegados)
            for p in recem_chegados:
                self.processos.remove(p)
            
            # Ordena a fila de prontos pelo tempo de chegada
            fila_prontos.sort(key=lambda x: x.tempo_chegada)
            
            if fila_prontos:
                processo_atual = fila_prontos.pop(0)
                
                # Calcula o tempo de espera
                processo_atual.tempo_espera = max(0, self.tempo_atual - processo_atual.tempo_chegada)
                
                # Executa o processo
                self.tempo_atual += processo_atual.tempo_execucao
                
                # Calcula o tempo de resposta total
                processo_atual.tempo_resposta_total = self.tempo_atual - processo_atual.tempo_chegada
                processo_atual.tempo_conclusao = self.tempo_atual
                
                self.processos_concluidos.append(processo_atual)
            else:
                # Sem processos disponíveis, avança o tempo
                self.tempo_atual += 1
        
        return self.calcular_metricas()

class EscalonadorSJF(EscalonadorBase):
    def executar(self, preemptivo=False):
        """
        Shortest Job First Scheduling
        
        :param preemptivo: Indica se usa SJF preemptivo ou não
        """
        fila_prontos = []
        while self.processos or fila_prontos:
            # Adiciona processos recém-chegados à fila de prontos
            recem_chegados = [p for p in self.processos if p.tempo_chegada <= self.tempo_atual]
            fila_prontos.extend(recem_chegados)
            for p in recem_chegados:
                self.processos.remove(p)
            
            # Ordena a fila de prontos pelo tempo de execução
            fila_prontos.sort(key=lambda x: x.tempo_execucao)
            
            if fila_prontos:
                processo_atual = fila_prontos.pop(0)
                
                # Calcula o tempo de espera
                processo_atual.tempo_espera = max(0, self.tempo_atual - processo_atual.tempo_chegada)
                
                # Executa o processo
                if preemptivo:
                    # No SJF preemptivo, verifica se um trabalho mais curto chega
                    trabalho_mais_curto = min(fila_prontos, key=lambda x: x.tempo_execucao) if fila_prontos else None
                    if trabalho_mais_curto and trabalho_mais_curto.tempo_execucao < processo_atual.tempo_execucao:
                        fila_prontos.append(processo_atual)
                        continue
                
                tempo_execucao = processo_atual.tempo_execucao
                self.tempo_atual += tempo_execucao
                processo_atual.tempo_execucao = 0
                
                # Calcula o tempo de resposta total
                processo_atual.tempo_resposta_total = self.tempo_atual - processo_atual.tempo_chegada
                processo_atual.tempo_conclusao = self.tempo_atual
                
                self.processos_concluidos.append(processo_atual)
            else:
                # Sem processos, avança o tempo
                self.tempo_atual += 1
        
        return self.calcular_metricas()

class EscalonadorRoundRobin(EscalonadorBase):
    def __init__(self, processos, quantum_tempo=2):
        """
        Round Robin Scheduling (Escalonamento por Turnos)
        
        :param processos: Lista de processos
        :param quantum_tempo: Fatia de tempo para cada processo
        """
        super().__init__(processos)
        self.quantum_tempo = quantum_tempo
    
    def executar(self):
        fila_prontos = []
        # Dicionário para rastrear se um processo já iniciou execução
        primeira_execucao = {}
        # Dicionário para rastrear o tempo em que o processo esteve pela última vez no CPU
        fim_ultima_execucao = {}
        
        while self.processos or fila_prontos:
            # Adiciona processos recém-chegados à fila de prontos
            recem_chegados = [p for p in self.processos if p.tempo_chegada <= self.tempo_atual]
            for p in recem_chegados:
                fila_prontos.append(p)
                self.processos.remove(p)
                # Inicializa o controlo de execução
                primeira_execucao[p.pid] = False
                fim_ultima_execucao[p.pid] = 0
            
            if fila_prontos:
                processo_atual = fila_prontos.pop(0)
                
                # Verifica se é a primeira vez que o processo está a executar
                if not primeira_execucao[processo_atual.pid]:
                    # Calcula o tempo de resposta (primeira vez que o processo obtém CPU)
                    processo_atual.tempo_resposta = self.tempo_atual - processo_atual.tempo_chegada
                    primeira_execucao[processo_atual.pid] = True
                
                # Calcula o tempo de espera desde a última execução
                if fim_ultima_execucao[processo_atual.pid] > 0:
                    processo_atual.tempo_espera += (self.tempo_atual - fim_ultima_execucao[processo_atual.pid])
                else:
                    # Primeira execução, o tempo de espera é o tempo desde a chegada
                    processo_atual.tempo_espera += (self.tempo_atual - processo_atual.tempo_chegada)
                
                # Executa o processo pelo quantum de tempo ou pelo tempo restante
                tempo_execucao = min(self.quantum_tempo, processo_atual.tempo_execucao)
                self.tempo_atual += tempo_execucao
                processo_atual.tempo_execucao -= tempo_execucao
                
                # Regista quando esta execução terminou
                fim_ultima_execucao[processo_atual.pid] = self.tempo_atual
                
                # Se o processo não estiver completo, volta para a fila
                if processo_atual.tempo_execucao > 0:
                    fila_prontos.append(processo_atual)
                else:
                    # Calcula o tempo de resposta total (tempo de conclusão - tempo de chegada)
                    processo_atual.tempo_resposta_total = self.tempo_atual - processo_atual.tempo_chegada
                    processo_atual.tempo_conclusao = self.tempo_atual
                    self.processos_concluidos.append(processo_atual)
            else:
                # Sem processos na fila de prontos, avança o tempo para próxima chegada
                if self.processos:
                    proxima_chegada = min(p.tempo_chegada for p in self.processos)
                    self.tempo_atual = max(self.tempo_atual + 1, proxima_chegada)
                else:
                    # Não há mais processos para executar
                    break
        
        return self.calcular_metricas()

    
import matplotlib.pyplot as plt

class SimuladorEscalonamento:
    def __init__(self, num_processos=10, taxa_chegada=0.5, distribuicao_execucao='exponential'):
        """
        Inicializa o simulador com configuração
        
        :param num_processos: Número de processos a gerar
        :param taxa_chegada: Taxa de chegada de Poisson
        :param distribuicao_execucao: Distribuição para tempos de execução
        """
        # Gera tempos de chegada
        tempos_chegada = GeradorProcessos.gerar_chegadas_poisson(
            taxa_chegada, num_processos)
        
        # Gera tempos de execução
        tempos_execucao = GeradorProcessos.gerar_tempos_execucao(
            distribuicao=distribuicao_execucao, 
            num_processos=num_processos)
        
        # Gera prioridades
        prioridades = GeradorProcessos.gerar_prioridades(num_processos)
        
        # Cria processos
        self.processos = [
            Processo(pid=i, 
                    tempo_chegada=tempos_chegada[i], 
                    tempo_execucao=tempos_execucao[i], 
                    prioridade=prioridades[i])
            for i in range(num_processos)
        ]
    
    def executar_simulacao(self):
        """
        Executa simulação com diferentes algoritmos de escalonamento
        
        :return: Dicionário com métricas para cada algoritmo
        """
        algoritmos = {
            'FCFS': EscalonadorFCFS,
            'SJF (Não Preemptivo)': EscalonadorSJF,
            'SJF (Preemptivo)': EscalonadorSJF,
            'Round Robin (Q=2)': EscalonadorRoundRobin,
        }
        
        resultados = {}
        for nome, classe_escalonador in algoritmos.items():
            # Copia profunda dos processos para garantir uma comparação justa
            copia_processos = [
                Processo(p.pid, p.tempo_chegada, p.tempo_execucao, p.prioridade) 
                for p in self.processos
            ]
            
            # Executa o escalonador
            if nome == 'SJF (Preemptivo)':
                metricas = classe_escalonador(copia_processos).executar(preemptivo=True)
            elif nome == 'Round Robin (Q=2)':
                metricas = classe_escalonador(copia_processos, quantum_tempo=2).executar()
            else:
                metricas = classe_escalonador(copia_processos).executar()
            
            resultados[nome] = metricas
        
        return resultados
    
    def visualizar_resultados(self, resultados):
        """
        Cria um gráfico de barras para comparar o desempenho dos algoritmos
        
        :param resultados: Dicionário com as métricas dos algoritmos
        """
        metricas = ['tempo_espera_medio', 'tempo_resposta_total_medio', 'taxa_processamento', 'utilizacao_cpu']
        
        plt.figure(figsize=(15, 10))
        
        for i, metrica in enumerate(metricas, 1):
            plt.subplot(2, 2, i)
            plt.title(f'{metrica.replace("_", " ").title()}')
            
            valores = [resultados[algo].get(metrica, 0) for algo in resultados]
            plt.bar(list(resultados.keys()), valores)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
        
        plt.show()

import argparse
import json
import sys

def analisar_argumentos():
    """Analisa os argumentos da linha de comando para o simulador de escalonamento"""
    parser = argparse.ArgumentParser(description='Simulador de Escalonamento de CPU')
    
    # Adiciona argumentos
    parser.add_argument('--num-processos', type=int, default=20,
                      help='Número de processos a simular')
    parser.add_argument('--taxa-chegada', type=float, default=0.5,
                      help='Taxa de chegada de Poisson')
    parser.add_argument('--distribuicao-execucao', choices=['exponential', 'normal'],
                      default='normal', help='Distribuição para tempos de execução')
    parser.add_argument('--config', type=str, 
                      help='Caminho para ficheiro de configuração JSON com parâmetros de simulação')
    parser.add_argument('--algoritmos', nargs='+', 
                      choices=['FCFS', 'SJF-NP', 'SJF-P', 'RR'],
                      default=['FCFS', 'SJF-NP', 'SJF-P', 'RR'],
                      help='Algoritmos de escalonamento a simular')
    parser.add_argument('--quantum-tempo', type=int, default=2,
                      help='Quantum de tempo para Round Robin')
    parser.add_argument('--sem-visualizacao', action='store_true',
                      help='Desativar visualização de resultados')
    
    return parser.parse_args()

def carregar_config(caminho_config):
    """Carrega parâmetros de simulação a partir de um ficheiro de configuração JSON"""
    try:
        with open(caminho_config, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar ficheiro de configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Analisa os argumentos da linha de comandos
    args = analisar_argumentos()
    
    # Se um ficheiro de configuração for fornecido, utiliza-o
    if args.config:
        config = carregar_config(args.config)
        num_processos = config.get('num_processos', 20)
        taxa_chegada = config.get('taxa_chegada', 0.5)
        distribuicao_execucao = config.get('distribuicao_execucao', 'normal')
        algoritmos_selecionados = config.get('algoritmos', ['FCFS', 'SJF-NP', 'SJF-P', 'RR'])
        quantum_tempo = config.get('quantum_tempo', 2)
        mostrar_visualizacao = not config.get('sem_visualizacao', False)
    else:
        # Utiliza os argumentos da linha de comandos
        num_processos = args.num_processos
        taxa_chegada = args.taxa_chegada
        distribuicao_execucao = args.distribuicao_execucao
        algoritmos_selecionados = args.algoritmos
        quantum_tempo = args.quantum_tempo
        mostrar_visualizacao = not args.sem_visualizacao
        
    # Define uma semente aleatória para garantir reprodutibilidade
    np.random.seed(42)
    
    # Cria o simulador
    simulador = SimuladorEscalonamento(
        num_processos=num_processos, 
        taxa_chegada=taxa_chegada, 
        distribuicao_execucao=distribuicao_execucao
    )
    
    # Mapear códigos de algoritmos para classes
    mapa_algoritmos = {
        'FCFS': {'classe': EscalonadorFCFS, 'params': {}},
        'SJF-NP': {'classe': EscalonadorSJF, 'params': {'preemptivo': False}},
        'SJF-P': {'classe': EscalonadorSJF, 'params': {'preemptivo': True}},
        'RR': {'classe': EscalonadorRoundRobin, 'params': {'quantum_tempo': quantum_tempo}}
    }
    
    # Filtra os algoritmos
    algoritmos_filtrados = {algo: mapa_algoritmos[algo] 
                          for algo in algoritmos_selecionados if algo in mapa_algoritmos}
    
    # Executa a simulação para os algoritmos selecionados
    resultados = {}
    for nome, config in algoritmos_filtrados.items():
        # Cópia profunda dos processos
        copia_processos = [
            Processo(p.pid, p.tempo_chegada, p.tempo_execucao, p.prioridade) 
            for p in simulador.processos
        ]
        
        # Cria instância do escalonador com os parâmetros
        classe_escalonador = config['classe']
        params = config['params']
        
        # Tratamento especial para o Round Robin que precisa do quantum de tempo no construtor
        if nome == 'RR':
            escalonador = classe_escalonador(copia_processos, **params)
            metricas = escalonador.executar()
        else:
            escalonador = classe_escalonador(copia_processos)
            metricas = escalonador.executar(**params)
        
        # Usar nome completo para exibição
        nome_completo = {
            'FCFS': 'First-Come, First-Served',
            'SJF-NP': 'Shortest Job First (Não Preemptivo)',
            'SJF-P': 'Shortest Job First (Preemptivo)',
            'RR': f'Round Robin (Q={quantum_tempo})'
        }
        
        resultados[nome_completo[nome]] = metricas
        
    # Imprimir resultados detalhados
    print("\nResultados da Simulação de Escalonamento de CPU:")
    print("=================================")
    print(f"Número de processos: {num_processos}")
    print(f"Taxa de chegada: {taxa_chegada}")
    print(f"Distribuição do tempo de execução: {distribuicao_execucao}")
    
    for algo, metricas in resultados.items():
        print(f"\nMétricas de {algo}:")
        nomes_metricas = {
            'tempo_espera_medio': 'Tempo médio de espera',
            'tempo_resposta_total_medio': 'Tempo médio de resposta total',
            'taxa_processamento': 'Taxa de processamento',
            'utilizacao_cpu': 'Utilização da CPU'
        }
        for metrica, valor in metricas.items():
            print(f"  {nomes_metricas.get(metrica, metrica)}: {valor:.2f}")
    
    # Visualizar resultados se solicitado
    if mostrar_visualizacao:
        simulador.visualizar_resultados(resultados)