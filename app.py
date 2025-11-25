"""
Parallel and Distributed Process Scheduling Simulator
Using Python and Streamlit for the web interface
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from queue import Queue
import socket
import json

# ==================== PROCESS MODEL ====================

@dataclass
class Processo:
    id: str
    tempoChegada: int
    duracaoCPU: int
    prioridade: int = 0
    tempoRestante: int = field(init=False)
    tempoEspera: int = 0
    tempoRetorno: int = 0
    tempoResposta: int = -1
    inicioExecucao: int = -1
    fimExecucao: int = -1
    
    def __post_init__(self):
        self.tempoRestante = self.duracaoCPU
    
    def reset(self):
        self.tempoRestante = self.duracaoCPU
        self.tempoEspera = 0
        self.tempoRetorno = 0
        self.tempoResposta = -1
        self.inicioExecucao = -1
        self.fimExecucao = -1
    
    def to_dict(self):
        return {
            'ID': self.id,
            'Chegada': self.tempoChegada,
            'Duração': self.duracaoCPU,
            'Prioridade': self.prioridade,
            'Espera': self.tempoEspera,
            'Retorno': self.tempoRetorno,
            'Resposta': self.tempoResposta if self.tempoResposta != -1 else '-',
        }

# ==================== SCHEDULING ALGORITHMS ====================

class Escalonador(ABC):
    def __init__(self, processos: List[Processo]):
        self.processos = [p for p in processos]
        self.for_reset = [p for p in processos]
        for p in self.processos:
            p.reset()
        self.timeline = []
        self.tempo_atual = 0
    
    @abstractmethod
    def proximo_processo(self, processos_prontos: List[Processo]) -> Processo:
        pass
    
    def simular(self):
        processos_nao_chegados = self.processos.copy()
        processos_prontos = []
        processos_executados = []
        
        while processos_nao_chegados or processos_prontos or any(p.tempoRestante > 0 for p in processos_executados):
            # Adicionar processos que chegaram
            processos_nao_chegados = [p for p in processos_nao_chegados if p.tempoChegada > self.tempo_atual]
            novos = [p for p in self.processos if p.tempoChegada == self.tempo_atual]
            processos_prontos.extend(novos)
            
            if processos_prontos:
                processo = self.proximo_processo(processos_prontos)
                processos_prontos.remove(processo)
                
                if processo.inicioExecucao == -1:
                    processo.inicioExecucao = self.tempo_atual
                    processo.tempoResposta = self.tempo_atual - processo.tempoChegada
                
                processo.tempoRestante -= 1
                self.timeline.append((self.tempo_atual, processo.id))
                
                if processo.tempoRestante == 0:
                    processo.fimExecucao = self.tempo_atual + 1
                    processo.tempoRetorno = processo.fimExecucao - processo.tempoChegada
                    processo.tempoEspera = processo.tempoRetorno - processo.duracaoCPU
                    processos_executados.append(processo)
            
            self.tempo_atual += 1
            
            if self.tempo_atual > 10000:  # Segurança
                break
        
        return self.processos, self.timeline

class EscalonadorFCFS(Escalonador):
    def proximo_processo(self, processos_prontos: List[Processo]) -> Processo:
        return min(processos_prontos, key=lambda p: p.tempoChegada)

class EscalonadorSJF(Escalonador):
    def proximo_processo(self, processos_prontos: List[Processo]) -> Processo:
        return min(processos_prontos, key=lambda p: p.tempoRestante)

class EscalonadorRoundRobin(Escalonador):
    def __init__(self, processos: List[Processo], quantum: int = 2):
        super().__init__(processos)
        self.quantum = quantum
        self.quantum_restante = 0
        self.processo_atual = None
    
    def proximo_processo(self, processos_prontos: List[Processo]) -> Processo:
        if self.processo_atual and self.processo_atual in processos_prontos and self.quantum_restante > 0:
            self.quantum_restante -= 1
            return self.processo_atual
        
        self.processo_atual = processos_prontos[0]
        self.quantum_restante = self.quantum - 1
        return self.processo_atual

class EscalonadorPrioridade(Escalonador):
    def proximo_processo(self, processos_prontos: List[Processo]) -> Processo:
        return min(processos_prontos, key=lambda p: p.prioridade)

# ==================== SIMULAÇÃO ====================

def executar_simulacao(processos: List[Processo], algoritmo: str, quantum: int = 2):
    if algoritmo == "FCFS":
        escalonador = EscalonadorFCFS(processos)
    elif algoritmo == "SJF":
        escalonador = EscalonadorSJF(processos)
    elif algoritmo == "Round Robin":
        escalonador = EscalonadorRoundRobin(processos, quantum)
    elif algoritmo == "Prioridade Preemptiva":
        escalonador = EscalonadorPrioridade(processos)
    
    processos_resultado, timeline = escalonador.simular()
    
    tempo_espera_medio = sum(p.tempoEspera for p in processos_resultado) / len(processos_resultado)
    tempo_retorno_medio = sum(p.tempoRetorno for p in processos_resultado) / len(processos_resultado)
    tempo_resposta_medio = sum(p.tempoResposta for p in processos_resultado if p.tempoResposta >= 0) / len([p for p in processos_resultado if p.tempoResposta >= 0])
    
    return processos_resultado, timeline, tempo_espera_medio, tempo_retorno_medio, tempo_resposta_medio

# ==================== VISUALIZAÇÃO ====================

def criar_gantt_chart(timeline, processos_dict):
    fig, ax = plt.subplots(figsize=(12, 4))
    
    processo_ids = list(set(p[1] for p in timeline))
    cores = {pid: f"C{i}" for i, pid in enumerate(processo_ids)}
    
    tempo_inicial = {}
    for tempo, pid in timeline:
        if pid not in tempo_inicial:
            tempo_inicial[pid] = tempo
    
    tempo_final = {}
    for tempo, pid in timeline:
        tempo_final[pid] = tempo + 1
    
    for pid in processo_ids:
        ax.barh(pid, tempo_final[pid] - tempo_inicial[pid], left=tempo_inicial[pid], 
               height=0.5, color=cores[pid], edgecolor='black')
    
    ax.set_xlabel('Tempo (unidades)')
    ax.set_ylabel('Processo')
    ax.set_title('Diagrama de Gantt')
    ax.grid(axis='x', alpha=0.3)
    
    return fig

# ==================== STREAMLIT APP ====================

def main():
    st.set_page_config(page_title="Process Scheduler Simulator", layout="wide")
    st.title("⏱️ Parallel and Distributed Process Scheduling Simulator")
    
    if 'processos' not in st.session_state:
        st.session_state.processos = []
    if 'resultados' not in st.session_state:
        st.session_state.resultados = {}
    
    tabs = st.tabs(["📥 Input Processes", "🚀 Simulation", "📊 Results", "📈 Comparison"])
    
    # TAB 1: Input Processes
    with tabs[0]:
        st.header("Add Processes")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            proc_id = st.text_input("Process ID", key="proc_id", value="")
        with col2:
            tempo_chegada = st.number_input("Arrival Time", min_value=0, key="chegada")
        with col3:
            duracao = st.number_input("CPU Duration (burst)", min_value=1, key="duracao")
        with col4:
            prioridade = st.number_input("Priority (lower = higher)", min_value=0, key="prioridade")
        
        if st.button("Add Process", use_container_width=True):
            if proc_id:
                novo_processo = Processo(
                    id=proc_id,
                    tempoChegada=int(tempo_chegada),
                    duracaoCPU=int(duracao),
                    prioridade=int(prioridade)
                )
                st.session_state.processos.append(novo_processo)
                st.success(f"Process {proc_id} added!")
                st.rerun()
        
        st.divider()
        
        if st.session_state.processos:
            st.subheader("Current Processes")
            df = pd.DataFrame([p.__dict__ for p in st.session_state.processos])
            st.dataframe(df, use_container_width=True)
            
            if st.button("Clear All Processes", use_container_width=True):
                st.session_state.processos = []
                st.rerun()
        else:
            st.info("No processes added yet. Add some to get started!")
        
        st.divider()
        st.subheader("Load from File")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file:
            df_upload = pd.read_csv(uploaded_file)
            for _, row in df_upload.iterrows():
                novo = Processo(
                    id=str(row['id']),
                    tempoChegada=int(row['tempoChegada']),
                    duracaoCPU=int(row['duracaoCPU']),
                    prioridade=int(row.get('prioridade', 0))
                )
                if novo not in st.session_state.processos:
                    st.session_state.processos.append(novo)
            st.success(f"Loaded {len(df_upload)} processes!")
            st.rerun()
    
    # TAB 2: Simulation
    with tabs[1]:
        st.header("Run Simulation")
        
        if not st.session_state.processos:
            st.warning("⚠️ Add processes first!")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                algoritmo = st.selectbox(
                    "Select Algorithm",
                    ["FCFS", "SJF", "Round Robin", "Prioridade Preemptiva"]
                )
            
            with col2:
                quantum = st.number_input("Quantum (for RR)", min_value=1, value=2)
            
            if st.button("Run Simulation", use_container_width=True, type="primary"):
                with st.spinner("Running simulation..."):
                    start_time = time.time()
                    
                    processos_copia = [Processo(
                        id=p.id,
                        tempoChegada=p.tempoChegada,
                        duracaoCPU=p.duracaoCPU,
                        prioridade=p.prioridade
                    ) for p in st.session_state.processos]
                    
                    resultado = executar_simulacao(processos_copia, algoritmo, int(quantum))
                    real_time = time.time() - start_time
                    
                    st.session_state.resultados[algoritmo] = {
                        'processos': resultado[0],
                        'timeline': resultado[1],
                        'espera_media': resultado[2],
                        'retorno_media': resultado[3],
                        'resposta_media': resultado[4],
                        'tempo_real': real_time
                    }
                    
                    st.success(f"✅ Simulation completed in {real_time:.4f}s")
    
    # TAB 3: Results
    with tabs[2]:
        st.header("Simulation Results")
        
        if not st.session_state.resultados:
            st.info("Run a simulation first!")
        else:
            algo_selecionado = st.selectbox(
                "Select Algorithm Results",
                list(st.session_state.resultados.keys())
            )
            
            resultado = st.session_state.resultados[algo_selecionado]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Wait Time", f"{resultado['espera_media']:.2f}")
            with col2:
                st.metric("Avg Return Time", f"{resultado['retorno_media']:.2f}")
            with col3:
                st.metric("Avg Response Time", f"{resultado['resposta_media']:.2f}")
            with col4:
                st.metric("Real Time (s)", f"{resultado['tempo_real']:.4f}")
            
            st.subheader("Process Metrics")
            df_resultado = pd.DataFrame([p.to_dict() for p in resultado['processos']])
            st.dataframe(df_resultado, use_container_width=True)
            
            st.subheader("Gantt Chart")
            fig = criar_gantt_chart(resultado['timeline'], {p.id: p for p in resultado['processos']})
            st.pyplot(fig)
    
    # TAB 4: Comparison
    with tabs[3]:
        st.header("Algorithm Comparison")
        
        if len(st.session_state.resultados) < 2:
            st.info("Run simulations with at least 2 algorithms to compare")
        else:
            comparacao_data = []
            for algo, resultado in st.session_state.resultados.items():
                comparacao_data.append({
                    'Algorithm': algo,
                    'Avg Wait': resultado['espera_media'],
                    'Avg Return': resultado['retorno_media'],
                    'Avg Response': resultado['resposta_media'],
                    'Real Time (s)': resultado['tempo_real']
                })
            
            df_comp = pd.DataFrame(comparacao_data)
            st.dataframe(df_comp, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig, ax = plt.subplots()
                df_comp.set_index('Algorithm')[['Avg Wait', 'Avg Return', 'Avg Response']].plot(kind='bar', ax=ax)
                ax.set_title('Scheduling Algorithms Comparison')
                ax.set_ylabel('Time Units')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            
            with col2:
                fig, ax = plt.subplots()
                df_comp.set_index('Algorithm')['Real Time (s)'].plot(kind='bar', color='coral', ax=ax)
                ax.set_title('Execution Time Comparison')
                ax.set_ylabel('Real Time (seconds)')
                plt.xticks(rotation=45)
                st.pyplot(fig)

if __name__ == "__main__":
    main()
