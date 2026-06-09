"""
brute_force.py
==============
Força Bruta — enumeração exaustiva de TODOS os caminhos simples.

Usado para instâncias PEQUENAS (N ≤ 12 vértices) como:
  - Validação do Dijkstra (os dois devem encontrar o mesmo custo ótimo)
  - Demonstração da explosão combinatória

Técnica: recursão com backtracking
  - A cada passo, tenta todos os vizinhos não visitados
  - Se chegar ao destino, registra o caminho
  - Desfaz a escolha (backtrack) e tenta outra direção

Autores: [Preencher RA – NOME]
"""


# =====================================================================
#  ENCONTRAR TODOS OS CAMINHOS (Backtracking)
# =====================================================================

def encontrar_todos_caminhos(grafo: dict, origem: int, destino: int) -> tuple:
    """
    Enumera TODOS os caminhos simples (sem repetir vértices) de
    'origem' até 'destino', usando recursão com backtracking.

    Parâmetros:
      grafo   : dict {id → [(vizinho, peso), ...]}
      origem  : id do vértice de partida
      destino : id do vértice de chegada

    Retorna:
      melhor_caminho : lista de ids do caminho de menor custo
      melhor_custo   : peso total do caminho ótimo
      todos_caminhos : lista de (caminho, custo) para TODOS os caminhos
      stats          : dict com contadores de operações
                       {"chamadas_recursivas": int, "caminhos_avaliados": int}
    """
    todos_caminhos = []
    # Usamos lista mutável para permitir atualização dentro da função aninhada
    stats = {"chamadas_recursivas": 0, "caminhos_avaliados": 0}

    def backtrack(atual, visitados, caminho_atual, custo_atual):
        """
        Função recursiva principal.

        atual         : nó que estamos visitando agora
        visitados     : SET de nós já no caminho atual (evita ciclos)
        caminho_atual : LIST do caminho parcial construído até aqui
        custo_atual   : custo acumulado até aqui
        """
        stats["chamadas_recursivas"] += 1

        # ── Caso base: chegamos ao destino ────────────────────────────
        if atual == destino:
            stats["caminhos_avaliados"] += 1
            # Salva uma CÓPIA do caminho (a lista será modificada depois)
            todos_caminhos.append((list(caminho_atual), custo_atual))
            return

        # ── Passo recursivo: tenta cada vizinho não visitado ──────────
        for vizinho, peso in grafo.get(atual, []):
            if vizinho not in visitados:
                # Faz a escolha
                visitados.add(vizinho)
                caminho_atual.append(vizinho)

                # Recursão — explora a partir do vizinho
                backtrack(vizinho, visitados, caminho_atual, custo_atual + peso)

                # BACKTRACK — desfaz a escolha para tentar outra direção
                caminho_atual.pop()
                visitados.discard(vizinho)

    # Inicia a busca a partir da origem
    visitados_iniciais = {origem}
    backtrack(origem, visitados_iniciais, [origem], 0.0)

    # ── Nenhum caminho encontrado ──────────────────────────────────────
    if not todos_caminhos:
        return None, float("inf"), [], stats

    # ── Encontra o caminho de MENOR custo (solução ótima global) ──────
    melhor = min(todos_caminhos, key=lambda x: x[1])
    return melhor[0], melhor[1], todos_caminhos, stats


# =====================================================================
#  FORÇA BRUTA PARA TODOS OS DESTINOS
# =====================================================================

def forca_bruta_todos_destinos(grafo: dict, vertices: dict, origem_id: int) -> dict:
    """
    Roda Força Bruta da 'origem' para TODOS os outros vértices.

    Parâmetros:
      grafo     : dict de adjacência
      vertices  : dict {id → tupla}
      origem_id : id do hub de origem

    Retorna:
      dict {destino_id: {"caminho", "custo", "stats", "nome"}}
    """
    resultado = {}
    for dest_id in grafo:
        if dest_id == origem_id:
            continue
        cam, custo, todos, stats = encontrar_todos_caminhos(
            grafo, origem_id, dest_id
        )
        resultado[dest_id] = {
            "caminho": cam,
            "custo":   custo,
            "todos":   todos,
            "stats":   stats,
            "nome":    vertices[dest_id][1] if dest_id in vertices else str(dest_id),
        }
    return resultado


# =====================================================================
#  DEMONSTRAÇÃO DA EXPLOSÃO COMBINATÓRIA
# =====================================================================

def contar_caminhos_por_n(tamanhos_n: list = None) -> list:
    """
    Para cada N em 'tamanhos_n', gera um grafo completo (todos os pares
    conectados) e conta o número de caminhos simples de 0 a N-1.

    Isso demonstra o crescimento FATORIAL do espaço de busca.

    Retorna lista de dicts {"N": int, "caminhos": int, "chamadas": int}
    """
    if tamanhos_n is None:
        tamanhos_n = [3, 4, 5, 6, 7, 8, 9, 10]

    resultados = []
    for n in tamanhos_n:
        # Grafo completo: cada nó conectado a todos os outros com peso 1
        grafo = {}
        for i in range(n):
            grafo[i] = [(j, 1.0) for j in range(n) if j != i]

        _, _, todos, stats = encontrar_todos_caminhos(grafo, 0, n - 1)
        resultados.append({
            "N":        n,
            "caminhos": stats["caminhos_avaliados"],
            "chamadas": stats["chamadas_recursivas"],
        })
        print(f"  N={n}: {stats['caminhos_avaliados']:6d} caminhos, "
              f"{stats['chamadas_recursivas']:8d} chamadas recursivas")

    return resultados


# =====================================================================
#  RELATÓRIO DA FORÇA BRUTA
# =====================================================================

def relatorio_forca_bruta(resultado_fb: dict, resultado_dijkstra: dict,
                           vertices: dict, hub_nome: str):
    """
    Imprime relatório comparando Força Bruta com Dijkstra.
    Verifica se os custos ótimos coincidem (validação cruzada).
    """
    print(f"\n{'='*60}")
    print(f"RELATÓRIO — Força Bruta vs Dijkstra | Hub: {hub_nome}")
    print(f"{'='*60}")
    print(f"{'Município':<22} {'FB Custo':>10} {'Dij Custo':>10} "
          f"{'Gap%':>8} {'Caminhos FB':>12}")
    print("-" * 65)

    gaps = []
    for dest_id, fb in resultado_fb.items():
        custo_fb  = fb["custo"]
        custo_dij = resultado_dijkstra.get(dest_id, {}).get("custo", float("inf"))
        nome      = fb["nome"]

        if custo_fb < float("inf") and custo_fb > 0:
            gap = abs(custo_dij - custo_fb) / custo_fb * 100
        else:
            gap = 0.0
        gaps.append(gap)

        caminhos = fb["stats"]["caminhos_avaliados"]
        print(f"{nome:<22} {custo_fb:>10.2f} {custo_dij:>10.2f} "
              f"{gap:>8.2f}% {caminhos:>12d}")

    media_gap = sum(gaps) / len(gaps) if gaps else 0
    print("-" * 65)
    print(f"Gap médio: {media_gap:.4f}% "
          f"(0% significa que Dijkstra é ÓTIMO para todos os destinos)")