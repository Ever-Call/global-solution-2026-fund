# 🌎 Global Solution 2026 — Sistema de Monitoramento de Riscos Ambientais

**FIAP • 1º Semestre 2026
Disciplina: Estruturas de Dados e Algoritmos (Dynamic Programming)**

---

## Descrição do Projeto

Este projeto propõe uma solução computacional para monitoramento, análise e priorização de riscos ambientais em municípios brasileiros, utilizando estruturas de dados e algoritmos clássicos para apoiar a tomada de decisão em cenários de emergência climática.

A aplicação integra:

🌐 Grafos Ponderados para representar municípios e suas conexões;
#
🌳 Árvore Binária de Busca (BST) para organizar e consultar níveis de risco;
#
⚡ Algoritmo de Dijkstra (Guloso) para cálculo de rotas mínimas;
#
🔍 Força Bruta (Backtracking) para validação da solução ótima;
#
📊 Monitoramento de desempenho com análise de tempo, memória e operações;
#
📈 Visualizações gráficas para interpretação dos resultados.

--- 

### Cenários implementados

| Cenário | Região | Objetivo | Peso das arestas |
|---------|--------|----------|-----------------|
| **A — Rio Grande do Sul** | 15 municípios afetados pelas enchentes 2024 | Menor rota de resposta a partir de Porto Alegre | Tempo (horas) |
| **B — MATOPIBA** | 12 municípios de MA/TO/PI/BA | Priorização de atendimento por risco de seca | Distância (km) |

---

## Estrutura do Repositório

```
global-solution-2026/
├── README.md                    ← Este arquivo
├── requirements.txt             ← Dependências Python
├── main.py                      ← Ponto de entrada: roda tudo
├── data/
│   ├── raw/
│   │   ├── municipios_rs.json       ← Municípios RS (15 nós)
│   │   ├── malha_viaria_rs.json     ← Malha viária RS
│   │   ├── municipios_matopiba.json ← Municípios MATOPIBA (12 nós)
│   │   └── malha_viaria_matopiba.json
│   └── processed/               ← Figuras geradas (PNG)
├── src/
│   ├── data_structures.py       ← Grafo, BST (Node + BinarySearchTree), FilaPrioridade
│   ├── brute_force.py           ← Backtracking com contadores de chamadas recursivas
│   ├── greedy.py                ← Dijkstra com heap + priorização por risco (BST)
│   ├── performance_monitor.py   ← Tempo (perf_counter), memória (tracemalloc), ops
│   └── visualizations.py        ← 5 figuras obrigatórias + escala de decisão
├── notebooks/
│   └── analise_resultados.ipynb ← Análise interativa e escala de decisão
├── tests/
│   └── test_algorithms.py       ← Testes unitários (unittest)
└── report/
    └── relatorio_final.pdf      ← Relatório técnico (gerado pelo main.py)
```

---

## Como Executar

### Pré-requisitos

```bash
pip install -r requirements.txt
```

### Executar tudo de uma vez

```bash
python main.py
```

Isso irá:
1. Carregar os dados dos dois cenários (RS e MATOPIBA)
2. Construir os grafos e BSTs
3. Rodar Força Bruta (N ≤ 12) e Dijkstra
4. Exibir relatório comparativo no terminal
5. Gerar as 6 figuras em `data/processed/`

### Executar testes

```bash
python tests/test_algorithms.py
```

---

## Módulos — Descrição

| Arquivo | Responsabilidade |
|---------|-----------------|
| `data_structures.py` | `construir_grafo()`, `BinarySearchTree` (inserir/buscar/remover/altura/in-order), `FilaPrioridade` |
| `brute_force.py` | `encontrar_todos_caminhos()` com backtracking, contadores, validação vs Dijkstra |
| `greedy.py` | `dijkstra()`, `reconstruir_caminho()`, `prioridade_por_risco()` com consulta à BST |
| `performance_monitor.py` | `MonitorDesempenho` (tracemalloc + perf_counter), `rodar_benchmark()` para N = 5..100 |
| `visualizations.py` | 6 figuras: grafo geográfico, BST, desempenho, tabela de estruturas, gap, escala |

---

## Dependências

```
matplotlib>=3.7
networkx>=3.1
```
---

## Conexão com ODS da ONU

| ODS | Conexão |
|-----|---------|
| **ODS 2** — Fome zero | Triagem de municípios agrícolas em risco de seca (MATOPIBA) |
| **ODS 9** — Infraestrutura | Otimização de rotas de atendimento com custo mínimo |
| **ODS 11** — Cidades sustentáveis | Resposta rápida a enchentes urbanas (RS) |
| **ODS 13** — Ação climática | Monitoramento contínuo de riscos ambientais via dados de satélite |

---

## 🧑‍💻 Integrantes do Grupo: 

| Nome            | RM       |
|-----------------|----------|
| Eduardo Francisco Mauro Gonçalves | RM561969 |
| Ever Callisaya Amaru | RM563971 |
| João Pedro Vieira Góes | RM564459 |
| Mateus Nunes Araujo | RM562008 |
| Matheus Henrique Ferreira Camargo da Silva | RM566232 |

---
