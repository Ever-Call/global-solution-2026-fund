"""
visualizations.py
=================
Gera as 5 figuras obrigatórias do projeto.

  Fig 1 — Grafo de municípios com caminhos mínimos (Dijkstra) destacados
  Fig 2 — Representação visual da BST (10–15 nós)
  Fig 3 — Gráfico comparativo de desempenho (Tempo × N)
  Fig 4 — Tabela de estruturas de dados utilizadas
  Fig 5 — Gráfico de gap de otimalidade

Cada figura inclui: título, legenda, fonte e interpretação no relatório.

Autores: [Preencher RA – NOME]
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

# Pasta onde as figuras serão salvas — caminho absoluto ancorado neste arquivo,
# funciona independente do diretório de trabalho (main.py, notebook, testes).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_FIGURAS = os.path.join(_ROOT, "data", "processed")
os.makedirs(PASTA_FIGURAS, exist_ok=True)


# =====================================================================
#  FIGURA 1 — GRAFO DE MUNICÍPIOS COM CAMINHOS DIJKSTRA DESTACADOS
# =====================================================================

def plotar_grafo(grafo: dict, vertices: dict, meta: dict,
                 resultado_dijkstra: dict, hub_id: int,
                 titulo: str, nome_arquivo: str):
    """
    Plota o grafo geográfico de municípios.

    Layout:
      - Posição dos nós: coordenadas geográficas reais (lon, lat)
      - Nós coloridos pelo índice de risco (vermelho = alto, azul = baixo)
      - Hub destacado em estrela amarela
      - Arestas do caminho mínimo (Dijkstra/SPT) em laranja
      - Demais rodovias em cinza claro

    Parâmetros:
      grafo             : dict de adjacência
      vertices          : dict {id → tupla}
      meta              : dict {id → {"lat", "lon", "hub"}}
      resultado_dijkstra: dict retornado por dijkstra_completo()
      hub_id            : id do vértice de origem
      titulo            : título exibido na figura
      nome_arquivo      : nome do arquivo de saída (ex: "fig1a.png")
    """
    G = nx.Graph()

    # ── Adiciona vértices ──────────────────────────────────────────────
    for vid in vertices:
        G.add_node(vid)

    # ── Adiciona arestas (sem duplicatas) ──────────────────────────────
    arestas_vistas = set()
    for u, vizinhos in grafo.items():
        for v, peso in vizinhos:
            chave = (min(u, v), max(u, v))
            if chave not in arestas_vistas:
                G.add_edge(u, v, peso=round(peso, 2))
                arestas_vistas.add(chave)

    # ── Identifica arestas que fazem parte de algum caminho mínimo ─────
    arestas_spt = set()
    for dest_id, info in resultado_dijkstra.items():
        cam = info.get("caminho", [])
        for i in range(len(cam) - 1):
            arestas_spt.add((min(cam[i], cam[i+1]), max(cam[i], cam[i+1])))

    # ── Posicionamento geográfico ──────────────────────────────────────
    pos = {}
    for vid in G.nodes():
        lon = meta[vid]["lon"]
        lat = meta[vid]["lat"]
        pos[vid] = (lon, lat)

    # ── Cores dos nós ─────────────────────────────────────────────────
    cores_nos    = []
    tamanhos_nos = []
    for vid in G.nodes():
        risco = vertices[vid][2]  # índice 2 = indice_risco na tupla
        if vid == hub_id:
            cores_nos.append("#FFD700")    # dourado para hub
            tamanhos_nos.append(800)
        else:
            # Gradiente: vermelho (risco alto) → azul (risco baixo)
            r = min(1.0, risco)
            g = 0.15
            b = max(0.0, 1 - risco)
            cores_nos.append((r, g, b))
            tamanhos_nos.append(350)

    # ── Cores das arestas ─────────────────────────────────────────────
    cores_arestas    = []
    espessuras       = []
    for u, v in G.edges():
        chave = (min(u, v), max(u, v))
        if chave in arestas_spt:
            cores_arestas.append("#FF7F00")  # laranja = caminho mínimo
            espessuras.append(3.5)
        else:
            cores_arestas.append("#CCCCCC")  # cinza = rodovia comum
            espessuras.append(1.0)

    # ── Rótulos dos nós ───────────────────────────────────────────────
    labels = {vid: vertices[vid][1][:9] for vid in G.nodes()}

    # ── Pesos das arestas ─────────────────────────────────────────────
    pesos_labels = nx.get_edge_attributes(G, "peso")

    # ── Plot ──────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(16, 11))

    # Hub como nó especial (estrela)
    outros  = [v for v in G.nodes() if v != hub_id]
    hub_nos = [hub_id] if hub_id in G.nodes() else []

    nx.draw_networkx_nodes(G, pos, nodelist=outros,
                           node_color=[cores_nos[list(G.nodes()).index(v)]
                                       for v in outros],
                           node_size=[tamanhos_nos[list(G.nodes()).index(v)]
                                      for v in outros],
                           node_shape="o", ax=ax)

    if hub_nos:
        nx.draw_networkx_nodes(G, pos, nodelist=hub_nos,
                               node_color=["#FFD700"],
                               node_size=[900],
                               node_shape="*", ax=ax)

    nx.draw_networkx_edges(G, pos,
                           edge_color=cores_arestas,
                           width=espessuras,
                           alpha=0.85, ax=ax)

    nx.draw_networkx_labels(G, pos, labels=labels,
                            font_size=7, font_weight="bold", ax=ax)

    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos_labels,
                                 font_size=6, ax=ax)

    # ── Legenda ───────────────────────────────────────────────────────
    patch_hub   = mpatches.Patch(color="#FFD700", label="Hub (origem)")
    patch_alto  = mpatches.Patch(color=(0.95, 0.15, 0.05), label="Risco alto")
    patch_baixo = mpatches.Patch(color=(0.3, 0.15, 0.7),  label="Risco baixo")
    patch_spt   = mpatches.Patch(color="#FF7F00", label="Caminho mínimo — Dijkstra (SPT)")
    patch_rest  = mpatches.Patch(color="#CCCCCC", label="Rodovias (demais)")

    ax.legend(handles=[patch_hub, patch_alto, patch_baixo, patch_spt, patch_rest],
              loc="best", fontsize=9)
    ax.set_title(f"{titulo}\nFonte: DNIT / Defesa Civil RS / INMET / IBGE",
                 fontsize=13, pad=12)
    ax.axis("off")

    plt.tight_layout()
    caminho = os.path.join(PASTA_FIGURAS, nome_arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[✓] Figura salva: {caminho}")


# =====================================================================
#  FIGURA 2 — VISUALIZAÇÃO DA BST
# =====================================================================

def _coletar_nos_bst(no, lista):
    """Coleta todos os nós da BST em in-order para posicionamento."""
    if no is None:
        return
    _coletar_nos_bst(no.esquerda, lista)
    lista.append(no)
    _coletar_nos_bst(no.direita, lista)


def _posicoes_hierarquicas(no, x=0.0, y=0.0, dx=3.0, posicoes=None):
    """
    Calcula coordenadas (x, y) para cada nó da BST.
    Usa layout hierárquico: raiz no topo, filhos abaixo.
    """
    if posicoes is None:
        posicoes = {}
    if no is None:
        return posicoes

    posicoes[id(no)] = (x, y)
    _posicoes_hierarquicas(no.esquerda, x - dx, y - 2, dx / 1.8, posicoes)
    _posicoes_hierarquicas(no.direita,  x + dx, y - 2, dx / 1.8, posicoes)
    return posicoes


def plotar_bst(bst, titulo: str, nome_arquivo: str):
    """
    Plota a Árvore Binária de Busca de municípios por risco.

    Layout:
      - Raiz no topo
      - Filhos à esquerda têm risco MENOR; à direita têm risco MAIOR
      - Nós coloridos pelo risco (vermelho = alto, azul = baixo)
      - Cada nó exibe: nome abreviado e índice de risco

    Parâmetros:
      bst          : BinarySearchTree já construída
      titulo       : título da figura
      nome_arquivo : nome do arquivo de saída
    """
    G = nx.DiGraph()

    def adicionar_nos(no):
        if no is None:
            return
        G.add_node(id(no))
        if no.esquerda:
            G.add_edge(id(no), id(no.esquerda))
            adicionar_nos(no.esquerda)
        if no.direita:
            G.add_edge(id(no), id(no.direita))
            adicionar_nos(no.direita)

    adicionar_nos(bst.raiz)
    pos = _posicoes_hierarquicas(bst.raiz, dx=3.5)

    # Coleta todos os nós em uma lista para acesso por id
    todos_nos = []
    _coletar_nos_bst(bst.raiz, todos_nos)
    mapa_nos = {id(n): n for n in todos_nos}

    # Rótulos: nome abreviado + risco
    labels = {}
    cores  = []
    for node_id in G.nodes():
        no = mapa_nos.get(node_id)
        if no:
            labels[node_id] = f"{no.nome[:11]}\nr={no.risco:.2f}"
            r = min(1.0, no.risco)
            cores.append((r, 0.1, max(0.0, 1 - r)))
        else:
            labels[node_id] = "?"
            cores.append((0.5, 0.5, 0.5))

    fig, ax = plt.subplots(figsize=(18, 9))

    nx.draw(G, pos=pos, labels=labels,
            node_color=cores, node_size=1800,
            font_size=7.5, font_weight="bold",
            arrows=True, arrowsize=18,
            arrowstyle="-|>",
            ax=ax)

    # Anotação explicativa
    ax.text(0.02, 0.02,
            "← Risco MENOR | Risco MAIOR →\n"
            "In-order = municípios em ordem crescente de risco",
            transform=ax.transAxes, fontsize=9,
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    ax.set_title(
        f"{titulo}\n"
        f"Altura da árvore: {bst.altura()} | "
        f"Fonte: IBGE / Defesa Civil / INMET",
        fontsize=12, pad=12
    )

    plt.tight_layout()
    caminho = os.path.join(PASTA_FIGURAS, nome_arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[✓] Figura salva: {caminho}")


# =====================================================================
#  FIGURA 3 — COMPARATIVO DE DESEMPENHO (Tempo × N)
# =====================================================================

def plotar_desempenho(resultados: list, nome_arquivo: str = "fig3_desempenho.png"):
    """
    Plota Tempo de Execução (ms) versus N para:
      - Força Bruta (pontos vermelhos, só para N ≤ 12)
      - Dijkstra    (pontos azuis, todos os N)

    Exibe linha vertical indicando o limite de viabilidade da FB.
    Escala logarítmica para melhor visualização da diferença.
    """
    ns_dij = [r["N"]           for r in resultados]
    ts_dij = [r["dijkstra_ms"] for r in resultados]
    ns_fb  = [r["N"]    for r in resultados if r["fb_ms"] is not None]
    ts_fb  = [r["fb_ms"]for r in resultados if r["fb_ms"] is not None]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ── Escala linear ─────────────────────────────────────────────────
    ax1.plot(ns_fb,  ts_fb,  "ro-", lw=2, ms=9, label="Força Bruta")
    ax1.plot(ns_dij, ts_dij, "bs-", lw=2, ms=9, label="Dijkstra (Guloso)")
    ax1.axvline(x=12, color="gray", ls="--", alpha=0.7, label="Limite FB (N=12)")
    ax1.fill_betweenx([min(ts_fb + ts_dij) * 0.9, max(ts_fb) * 1.1],
                       12, 13, alpha=0.1, color="red",
                       label="FB inviável →")
    ax1.set_xlabel("Número de vértices (N)", fontsize=11)
    ax1.set_ylabel("Tempo (ms)", fontsize=11)
    ax1.set_title("Escala Linear", fontsize=11)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # ── Escala logarítmica ────────────────────────────────────────────
    ax2.semilogy(ns_fb,  ts_fb,  "ro-", lw=2, ms=9, label="Força Bruta")
    ax2.semilogy(ns_dij, ts_dij, "bs-", lw=2, ms=9, label="Dijkstra (Guloso)")
    ax2.axvline(x=12, color="gray", ls="--", alpha=0.7, label="Limite FB")
    ax2.set_xlabel("Número de vértices (N)", fontsize=11)
    ax2.set_ylabel("Tempo (ms) — log", fontsize=11)
    ax2.set_title("Escala Logarítmica (evidencia a diferença)", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, which="both")

    fig.suptitle(
        "Comparativo de Desempenho: Força Bruta vs Dijkstra\n"
        "A Força Bruta explode exponencialmente; Dijkstra cresce suavemente\n"
        "Fonte: Grafos sintéticos — performance_monitor.py (seed=42)",
        fontsize=12
    )
    plt.tight_layout()
    caminho = os.path.join(PASTA_FIGURAS, nome_arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[✓] Figura salva: {caminho}")


# =====================================================================
#  FIGURA 4 — TABELA DE ESTRUTURAS DE DADOS
# =====================================================================

def plotar_tabela_estruturas(nome_arquivo: str = "fig4_tabela_estruturas.png"):
    """
    Gera uma tabela visual mostrando cada estrutura de dados,
    onde ela é usada e sua complexidade.
    """
    colunas = ["Estrutura", "Usado em", "Onde no código", "Complexidade"]
    linhas = [
        ["list",       "Adjacência do grafo;\nresultado do caminho",
         "grafo[u] = [(v, peso)]\ncaminho = [n1, n2, ...]",
         "Espaço: O(V+E)"],
        ["tuple",      "Dados do vértice;\naresta (u,v,peso)",
         "vertices[id] = (id, nome,\nrisco, custo, pop)",
         "Acesso: O(1)"],
        ["dict",       "Mapa id→vértice;\ndist[] e anterior[]",
         "dist = {v: INF}\nanterior = {v: None}",
         "Busca: O(1) médio"],
        ["set",        "Nós visitados;\nprevine ciclos",
         "visitados = set()\nvisitados.add(u)",
         "Pertencimento: O(1)"],
        ["heapq\n(heap)",  "Fila de prioridade\nno Dijkstra",
         "heapq.heappush(heap,\n(custo, id))",
         "Inserção/Extração:\nO(log V)"],
        ["BST\n(manual)",  "Classificar por risco;\nbusca por intervalo",
         "bst.inserir()\nbst.buscar(r_min, r_max)",
         "Busca/Inserção:\nO(h), h = altura"],
        ["grafo\n(dict+list)", "Rede de municípios;\nrotas de atendimento",
         "grafo = {id: [(viz,peso)]}\nAdjacência esparsa",
         "Espaço: O(V+E)\nDijkstra: O((V+E)logV)"],
    ]

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.axis("off")

    tabela = ax.table(
        cellText=linhas,
        colLabels=colunas,
        cellLoc="left",
        loc="center",
        colWidths=[0.13, 0.22, 0.34, 0.21],
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(8.5)
    tabela.scale(1, 2.8)

    # Cabeçalho azul escuro
    for j in range(len(colunas)):
        tabela[0, j].set_facecolor("#1a5276")
        tabela[0, j].set_text_props(color="white", fontweight="bold")

    # Linhas alternadas: azul claro / branco
    for i in range(1, len(linhas) + 1):
        cor = "#eaf4fb" if i % 2 == 0 else "white"
        for j in range(len(colunas)):
            tabela[i, j].set_facecolor(cor)

    ax.set_title(
        "Estruturas de Dados Utilizadas no Projeto\n"
        "Fonte: Implementação própria — src/data_structures.py, greedy.py, brute_force.py",
        fontsize=12, pad=20
    )

    plt.tight_layout()
    caminho = os.path.join(PASTA_FIGURAS, nome_arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[✓] Figura salva: {caminho}")


# =====================================================================
#  FIGURA 5 — GAP DE OTIMALIDADE E EXPLOSÃO COMBINATÓRIA
# =====================================================================

def plotar_gap_otimalidade(resultados: list, nome_arquivo: str = "fig5_gap.png"):
    """
    Duas sub-figuras:
      Esq: Chamadas recursivas da FB por N (evidencia explosão)
      Dir: Gap (%) entre FB e Dijkstra por N (deve ser sempre 0%)
    """
    # Filtra só os N onde rodamos FB
    ns       = [r["N"]              for r in resultados if r["fb_ms"] is not None]
    chamadas = [r["fb_chamadas_rec"] for r in resultados if r["fb_ms"] is not None]
    gaps     = [r["gap_pct"]         for r in resultados if r["fb_ms"] is not None]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ── Chamadas recursivas ───────────────────────────────────────────
    bars = ax1.bar(ns, chamadas, color="#c0392b", alpha=0.85, width=0.6)
    ax1.set_xlabel("Número de vértices (N)", fontsize=11)
    ax1.set_ylabel("Chamadas recursivas (FB)", fontsize=11)
    ax1.set_title("Explosão Combinatória — Força Bruta\n"
                  "(mais nós = muito mais chamadas)", fontsize=11)
    ax1.grid(True, axis="y", alpha=0.3)
    # Rótulos nas barras
    for bar, c in zip(bars, chamadas):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + max(chamadas) * 0.01,
                 f"{c:,}", ha="center", va="bottom", fontsize=9)

    # ── Gap de otimalidade ────────────────────────────────────────────
    ax2.bar(ns, gaps, color="#27ae60", alpha=0.85, width=0.6)
    ax2.set_xlabel("Número de vértices (N)", fontsize=11)
    ax2.set_ylabel("Gap de otimalidade (%)", fontsize=11)
    ax2.set_title("Gap: Dijkstra vs Força Bruta\n"
                  "0% = Dijkstra encontra a solução ótima", fontsize=11)
    ax2.set_ylim(0, max(gaps) + 1 if any(g > 0 for g in gaps) else 5)
    ax2.grid(True, axis="y", alpha=0.3)

    # Caixa de destaque
    ax2.text(
        0.5, 0.55,
        "Gap = 0%\npara todos os N\n\nDijkstra é\nGARANTIDO ÓTIMO\npara caminho mínimo",
        transform=ax2.transAxes, ha="center", va="center",
        fontsize=12, color="#145a32",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#d5f5e3", alpha=0.9)
    )

    fig.suptitle(
        "Gap de Otimalidade e Explosão Combinatória\n"
        "Fonte: Testes com grafos sintéticos — performance_monitor.py",
        fontsize=12
    )
    plt.tight_layout()
    caminho = os.path.join(PASTA_FIGURAS, nome_arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[✓] Figura salva: {caminho}")


# =====================================================================
#  ESCALA DE DECISÃO
# =====================================================================

def plotar_escala_decisao(nome_arquivo: str = "fig6_escala_decisao.png"):
    """
    Plota a Escala de Decisão com 4 níveis, comparando soluções
    em qualidade, custo computacional e aplicabilidade.
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.axis("off")

    colunas = ["Nível", "Solução", "Qualidade\nda Solução",
               "Custo\nComputacional", "Aplicabilidade\nPrática"]
    linhas = [
        ["★★★★\n(Ótimo)",
         "Dijkstra — N=15 (RS)\nN=12 (MATOPIBA)",
         "100% ótima\n(gap=0%)",
         "Baixo\nO((V+E)logV)",
         "RECOMENDADO\nResponde em <1ms"],
        ["★★★☆\n(Muito Bom)",
         "Dijkstra — instâncias maiores\n(N=50, N=100)",
         "100% ótima\n(gap=0%)",
         "Moderado\n(ms a segundos)",
         "Viável para redes\nnacionais ampliadas"],
        ["★★☆☆\n(Aceitável)",
         "Força Bruta — N≤10",
         "100% ótima\n(gap=0%)",
         "Alto\nexplosão exponencial",
         "Apenas para validação\ne instâncias de teste"],
        ["★☆☆☆\n(Inviável)",
         "Força Bruta — N>12",
         "Ótima (teórica)\nmas nunca termina",
         "Inviável\nO(n!) ou O(2ⁿ)",
         "NÃO USAR em produção\ntempo infinito na prática"],
    ]

    tabela = ax.table(
        cellText=linhas, colLabels=colunas,
        cellLoc="center", loc="center",
        colWidths=[0.12, 0.24, 0.18, 0.18, 0.22],
    )
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(9)
    tabela.scale(1, 3.5)

    # Cores do cabeçalho
    for j in range(len(colunas)):
        tabela[0, j].set_facecolor("#1a5276")
        tabela[0, j].set_text_props(color="white", fontweight="bold")

    # Cores por nível
    cores_niveis = ["#d5f5e3", "#fef9e7", "#fdebd0", "#fadbd8"]
    for i in range(1, 5):
        for j in range(len(colunas)):
            tabela[i, j].set_facecolor(cores_niveis[i - 1])

    ax.set_title(
        "Escala de Decisão — Trade-off Qualidade × Custo Computacional\n"
        "Fonte: Análise comparativa FB vs Dijkstra — Global Solution 2026",
        fontsize=12, pad=15
    )

    plt.tight_layout()
    caminho = os.path.join(PASTA_FIGURAS, nome_arquivo)
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[✓] Figura salva: {caminho}")