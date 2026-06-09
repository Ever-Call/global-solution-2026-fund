"""
greedy.py
=========
Algoritmo Guloso — DIJKSTRA (Variante C escolhida pelo grupo)

Por que Dijkstra é um algoritmo Guloso?
  A cada iteração, escolhemos a decisão LOCALMENTE ÓTIMA:
  extrair o vértice não visitado com MENOR custo acumulado.
  Essa escolha local garante a solução GLOBALMENTE ÓTIMA
  (prova: a distância já fixada nunca precisa ser atualizada).

Aplicação no projeto:
  Cenário A (RS)       → peso = tempo (horas) | Hub: Porto Alegre
  Cenário B (MATOPIBA) → peso = distância (km) | Hub: Palmas

Complexidade: O((V + E) · log V) com heap binário

Autores: [Preencher RA – NOME]
"""

import heapq


# =====================================================================
#  DIJKSTRA — caminho mínimo de fonte única
# =====================================================================

def dijkstra(grafo: dict, origem: int) -> tuple:
    """
    Algoritmo de Dijkstra com heap (heapq).

    Estruturas usadas:
      dist      → dict  {id: custo}   — menor custo até cada vértice
      anterior  → dict  {id: id_pai}  — predecessor no caminho ótimo
      heap      → list  [(custo, id)] — fila de prioridade (min-heap)
      visitados → set   de vértices finalizados (custo definitivo)
      ops       → int   de arestas relaxadas (métrica de desempenho)

    Parâmetros:
      grafo  : dict {id → [(vizinho, peso), ...]}
      origem : id do vértice inicial

    Retorna:
      dist     : dict com menor custo até cada vértice
      anterior : dict para reconstruir o caminho ótimo
      ops      : número de arestas relaxadas (operações elementares)
    """
    INF = float("inf")

    # ── Inicialização ─────────────────────────────────────────────────
    dist     = {v: INF for v in grafo}  # todos infinitos no início
    dist[origem] = 0.0                  # custo até a origem é zero

    anterior = {v: None for v in grafo} # nenhum predecessor ainda

    heap     = [(0.0, origem)]          # começa com a origem no heap
    visitados = set()                   # conjunto vazio de finalizados
    ops       = 0                       # contador de operações

    # ── Loop principal ────────────────────────────────────────────────
    while heap:
        custo_atual, u = heapq.heappop(heap)  # extrai o de menor custo

        # Se já foi finalizado, descarta (pode haver duplicatas no heap)
        if u in visitados:
            continue
        visitados.add(u)  # marca como finalizado

        # ── Relaxamento de arestas ────────────────────────────────────
        # Para cada vizinho v de u: verifica se vale a pena
        # ir de 'origem' até 'v' passando por 'u'
        for vizinho, peso in grafo.get(u, []):
            ops += 1  # conta cada aresta relaxada
            novo_custo = custo_atual + peso

            if novo_custo < dist[vizinho]:
                # Encontramos um caminho MELHOR até 'vizinho'!
                dist[vizinho]     = novo_custo
                anterior[vizinho] = u           # u é o melhor predecessor
                heapq.heappush(heap, (novo_custo, vizinho))

    return dist, anterior, ops


# =====================================================================
#  RECONSTRUÇÃO DO CAMINHO
# =====================================================================

def reconstruir_caminho(anterior: dict, origem: int, destino: int) -> list:
    """
    Reconstrói o caminho ótimo do 'origem' ao 'destino'
    percorrendo o dicionário 'anterior' de trás para frente.

    Retorna lista de ids [origem, ..., destino] ou [] se não há caminho.
    """
    caminho = []
    atual   = destino

    while atual is not None:
        caminho.append(atual)
        atual = anterior[atual]

    caminho.reverse()  # estava ao contrário

    # Verifica se o caminho realmente começa na origem
    if not caminho or caminho[0] != origem:
        return []
    return caminho


# =====================================================================
#  DIJKSTRA COMPLETO (para todos os destinos)
# =====================================================================

def dijkstra_completo(grafo: dict, vertices: dict, origem_id: int) -> tuple:
    """
    Roda Dijkstra uma vez e retorna o resultado para TODOS os destinos.

    Parâmetros:
      grafo     : dict de adjacência
      vertices  : dict {id → tupla (id, nome, risco, custo, pop)}
      origem_id : id do hub de partida

    Retorna:
      resultado : dict {dest_id: {"caminho", "custo", "nome"}}
      ops       : total de arestas relaxadas
    """
    dist, anterior, ops = dijkstra(grafo, origem_id)

    resultado = {}
    for dest_id in grafo:
        if dest_id == origem_id:
            continue
        caminho = reconstruir_caminho(anterior, origem_id, dest_id)
        resultado[dest_id] = {
            "caminho": caminho,
            "custo":   dist[dest_id],
            "nome":    vertices[dest_id][1] if dest_id in vertices else str(dest_id),
        }

    return resultado, ops


# =====================================================================
#  PRIORIZAÇÃO POR RISCO (usa BST para filtrar municípios críticos)
# =====================================================================

def prioridade_por_risco(resultado: dict, bst, limiar_risco: float = 0.75) -> list:
    """
    Usa a BST para consultar municípios de alto risco e ordena
    pelo critério: MAIOR RISCO primeiro; empate → MENOR rota.

    Esta é a lista de atendimento prioritário recomendada pelo sistema.

    Parâmetros:
      resultado     : dict retornado por dijkstra_completo()
      bst           : BinarySearchTree já construída
      limiar_risco  : municípios com risco >= limiar são priorizados

    Retorna:
      lista de dicts [{"id_ibge", "nome", "risco", "custo_rota", "caminho"}]
      ordenada por prioridade de atendimento
    """
    # Consulta BST: municípios com risco entre limiar e 1.0
    nos_alto_risco = bst.buscar(limiar_risco, 1.0)
    ids_alto_risco = {n.id_ibge: n for n in nos_alto_risco}

    priorizados = []
    for dest_id, info in resultado.items():
        if dest_id in ids_alto_risco:
            no = ids_alto_risco[dest_id]
            priorizados.append({
                "id_ibge":    dest_id,
                "nome":       info["nome"],
                "risco":      no.risco,
                "custo_rota": info["custo"],
                "caminho":    info["caminho"],
            })

    # Ordena: maior risco primeiro; empate → menor custo de rota
    priorizados.sort(key=lambda x: (-x["risco"], x["custo_rota"]))
    return priorizados


# =====================================================================
#  DEMONSTRAÇÃO DO CRITÉRIO GULOSO (a cada passo)
# =====================================================================

def dijkstra_passo_a_passo(grafo: dict, origem: int, vertices: dict) -> list:
    """
    Versão "verbose" do Dijkstra que mostra a decisão gulosa a cada passo.
    Útil para entender por que a escolha local é ótima.

    Retorna lista de passos [{passo, no_escolhido, custo, vizinhos_relaxados}]
    """
    INF = float("inf")
    dist     = {v: INF for v in grafo}
    dist[origem] = 0.0
    anterior = {v: None for v in grafo}
    heap     = [(0.0, origem)]
    visitados = set()
    passos   = []

    while heap:
        custo_atual, u = heapq.heappop(heap)
        if u in visitados:
            continue
        visitados.add(u)

        nome_u = vertices[u][1] if u in vertices else str(u)
        vizinhos_relaxados = []

        for vizinho, peso in grafo.get(u, []):
            novo_custo = custo_atual + peso
            if novo_custo < dist[vizinho]:
                dist[vizinho]     = novo_custo
                anterior[vizinho] = u
                heapq.heappush(heap, (novo_custo, vizinho))
                nome_v = vertices[vizinho][1] if vizinho in vertices else str(vizinho)
                vizinhos_relaxados.append({
                    "nome": nome_v,
                    "novo_custo": round(novo_custo, 2),
                })

        passos.append({
            "passo":         len(passos) + 1,
            "no_escolhido":  nome_u,
            "custo":         round(custo_atual, 2),
            "relaxamentos":  vizinhos_relaxados,
        })

    return passos