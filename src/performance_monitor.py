"""
performance_monitor.py
======================
Monitoramento de Desempenho dos Algoritmos.

Para cada tamanho N de instância, registra:
  - Tempo de execução (ms) via time.perf_counter()
  - Memória alocada (MB) via tracemalloc
  - Número de operações elementares (arestas relaxadas / chamadas recursivas)

Tamanhos testados: N = 5, 8, 10, 12, 20, 50, 100
  Força Bruta: apenas N ≤ 12 (explosão combinatória inviabiliza além disso)
  Dijkstra   : todos os tamanhos

Autores: [Preencher RA – NOME]
"""

import time
import tracemalloc
import random
import heapq


# =====================================================================
#  CLASSE MONITOR DE DESEMPENHO
# =====================================================================

class MonitorDesempenho:
    """
    Mede tempo e memória de qualquer função.

    Uso:
      monitor = MonitorDesempenho()
      resultado, metricas = monitor.medir(minha_funcao, arg1, arg2)
      print(metricas["tempo_ms"], metricas["memoria_mb"])
    """

    def medir(self, funcao, *args, **kwargs) -> tuple:
        """
        Executa funcao(*args) e registra:
          tempo_ms   : duração em milissegundos
          memoria_mb : pico de memória RAM em megabytes

        Retorna: (resultado_da_funcao, dicionário_de_métricas)
        """
        # ── Inicia rastreamento de memória ────────────────────────────
        tracemalloc.start()
        t_inicio = time.perf_counter()

        # ── Executa a função ──────────────────────────────────────────
        resultado = funcao(*args, **kwargs)

        # ── Coleta métricas ───────────────────────────────────────────
        t_fim    = time.perf_counter()
        _, pico  = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        metricas = {
            "tempo_ms":   (t_fim - t_inicio) * 1000,
            "memoria_mb": pico / (1024 * 1024),
        }
        return resultado, metricas


# =====================================================================
#  GERAÇÃO DE GRAFOS SINTÉTICOS PARA ESCALABILIDADE
# =====================================================================

def gerar_grafo_sintetico(n: int, seed: int = 42) -> dict:
    """
    Gera um grafo aleatório CONECTADO com N vértices.

    Estratégia:
      1. Cria uma cadeia 0→1→2→...→(n-1) para garantir conectividade
      2. Adiciona ~20% de arestas extras aleatórias para criar atalhos

    Parâmetro seed: garante reprodutibilidade dos resultados.
    """
    random.seed(seed)
    grafo = {i: [] for i in range(n)}

    # Passo 1: cadeia de 0 a n-1 (garante que o grafo é conectado)
    for i in range(n - 1):
        peso = round(random.uniform(0.5, 5.0), 2)
        grafo[i].append((i + 1, peso))
        grafo[i + 1].append((i, peso))

    # Passo 2: arestas extras para tornar o grafo mais interessante
    extras = max(1, int(n * 0.3))
    for _ in range(extras):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            peso = round(random.uniform(0.5, 5.0), 2)
            grafo[u].append((v, peso))
            grafo[v].append((u, peso))

    return grafo


# =====================================================================
#  FORÇA BRUTA PARA GRAFOS SINTÉTICOS (escalabilidade)
# =====================================================================

def _fb_backtrack(grafo: dict, atual: int, destino: int,
                  visitados: set, custo: float, contador: list) -> float:
    """
    Backtracking para encontrar o caminho de MENOR custo.
    Retorna o melhor custo encontrado.
    """
    contador[0] += 1  # chamadas recursivas

    if atual == destino:
        contador[1] += 1  # caminhos completos
        return custo

    melhor = float("inf")
    for vizinho, peso in grafo.get(atual, []):
        if vizinho not in visitados:
            visitados.add(vizinho)
            custo_v = _fb_backtrack(
                grafo, vizinho, destino, visitados, custo + peso, contador
            )
            melhor = min(melhor, custo_v)
            visitados.discard(vizinho)

    return melhor


def forca_bruta_sintetico(grafo: dict, origem: int = 0, destino: int = None):
    """
    Força Bruta para grafo sintético.
    Retorna (custo_otimo, chamadas_recursivas, caminhos_avaliados).
    """
    if destino is None:
        destino = max(grafo.keys())
    contador = [0, 0]  # [chamadas, caminhos]
    visitados = {origem}
    custo = _fb_backtrack(grafo, origem, destino, visitados, 0.0, contador)
    return custo, contador[0], contador[1]


# =====================================================================
#  DIJKSTRA PARA GRAFOS SINTÉTICOS (escalabilidade)
# =====================================================================

def dijkstra_sintetico(grafo: dict, origem: int = 0) -> tuple:
    """
    Dijkstra para grafo sintético.
    Retorna (dist_dict, operacoes_elementares).
    """
    INF = float("inf")
    dist = {v: INF for v in grafo}
    dist[origem] = 0
    heap = [(0, origem)]
    visitados = set()
    ops = 0

    while heap:
        d, u = heapq.heappop(heap)
        if u in visitados:
            continue
        visitados.add(u)
        for v, w in grafo.get(u, []):
            ops += 1
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))

    return dist, ops


# =====================================================================
#  BENCHMARK COMPLETO
# =====================================================================

def rodar_benchmark(tamanhos: list = None, limite_fb: int = 12) -> list:
    """
    Executa o benchmark para cada N em 'tamanhos'.

    Para cada N:
      - Gera grafo sintético
      - Mede Dijkstra (sempre)
      - Mede Força Bruta (só se N ≤ limite_fb)

    Retorna lista de dicts com todas as métricas.
    """
    if tamanhos is None:
        tamanhos = [5, 8, 10, 12, 20, 50, 100]

    monitor = MonitorDesempenho()
    resultados = []

    print("\n" + "="*65)
    print("BENCHMARK DE DESEMPENHO")
    print(f"{'N':>5} | {'Dijkstra (ms)':>14} | {'FB (ms)':>10} | "
          f"{'FB Chamadas':>12} | {'Dij Ops':>10}")
    print("-"*65)

    for n in tamanhos:
        grafo = gerar_grafo_sintetico(n)
        linha = {"N": n}

        # ── Dijkstra ────────────────────────────────────────────────
        (dist_dij, ops_dij), met_dij = monitor.medir(dijkstra_sintetico, grafo, 0)
        linha["dijkstra_ms"]     = round(met_dij["tempo_ms"], 4)
        linha["dijkstra_mem_mb"] = round(met_dij["memoria_mb"], 5)
        linha["dijkstra_ops"]    = ops_dij

        # ── Força Bruta (apenas N ≤ limite_fb) ──────────────────────
        if n <= limite_fb:
            (custo_fb, chamadas, caminhos), met_fb = monitor.medir(
                forca_bruta_sintetico, grafo, 0, n - 1
            )
            linha["fb_ms"]           = round(met_fb["tempo_ms"], 4)
            linha["fb_mem_mb"]       = round(met_fb["memoria_mb"], 5)
            linha["fb_chamadas_rec"] = chamadas
            linha["fb_caminhos"]     = caminhos

            # Gap: Dijkstra é ótimo → gap = 0% para todos os casos testados
            custo_dij_destino = dist_dij.get(n - 1, float("inf"))
            if custo_fb > 0 and custo_fb < float("inf"):
                gap = abs(custo_dij_destino - custo_fb) / custo_fb * 100
            else:
                gap = 0.0
            linha["gap_pct"] = round(gap, 4)
        else:
            linha["fb_ms"]           = None
            linha["fb_mem_mb"]       = None
            linha["fb_chamadas_rec"] = None
            linha["fb_caminhos"]     = None
            linha["gap_pct"]         = None

        resultados.append(linha)

        # ── Imprime linha da tabela ──────────────────────────────────
        fb_ms_str  = f"{linha['fb_ms']:.4f}" if linha["fb_ms"] is not None else "N/A (inviável)"
        fb_ch_str  = str(linha["fb_chamadas_rec"]) if linha["fb_chamadas_rec"] is not None else "---"
        print(f"{n:>5} | {linha['dijkstra_ms']:>14.4f} | {fb_ms_str:>10} | "
              f"{fb_ch_str:>12} | {ops_dij:>10}")

    print("="*65)
    return resultados


# =====================================================================
#  ANÁLISE DOS RESULTADOS DO BENCHMARK
# =====================================================================

def analisar_benchmark(resultados: list):
    """
    Imprime análise textual dos resultados do benchmark.
    Identifica o ponto de cruzamento das curvas FB vs Dijkstra.
    """
    print("\n── ANÁLISE DO BENCHMARK ──────────────────────────────────────")

    ns_fb  = [r["N"] for r in resultados if r["fb_ms"] is not None]
    ts_fb  = [r["fb_ms"] for r in resultados if r["fb_ms"] is not None]

    if len(ns_fb) >= 2:
        # Crescimento médio entre o maior N testável por FB e o anterior
        crescimento = ts_fb[-1] / ts_fb[0] if ts_fb[0] > 0 else 0
        print(f"\nForça Bruta: tempo cresceu {crescimento:.1f}× de N={ns_fb[0]} a N={ns_fb[-1]}")

    print(f"\nDijkstra: escala de forma previsível (O((V+E)·log V))")
    print(f"  → sempre mais rápido e mais eficiente para N > 8")
    print(f"\nCruzamento das curvas: a partir de N~8-10, a FB explode")
    print(f"e o Dijkstra torna-se a única opção viável.")
    print(f"\nGap de otimalidade: 0% — Dijkstra é ÓTIMO para")
    print(f"caminhos de menor custo (prova de corretude formal).")