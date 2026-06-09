"""
main.py
=======
Ponto de entrada do sistema de Monitoramento de Riscos Ambientais.

Executa em sequência:
  1. Carrega dados dos dois cenários (RS e MATOPIBA)
  2. Constrói grafo e BST para cada cenário
  3. Roda Dijkstra (Guloso) para todos os destinos
  4. Roda Força Bruta (validação, N ≤ 12) e compara com Dijkstra
  5. Benchmark de desempenho com grafos sintéticos (N = 5..100)
  6. Gera todas as figuras obrigatórias em data/processed/
Uso:
  python main.py

Autores: [Preencher RA – NOME]
"""

import os
import sys

# Adiciona src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_structures import (
    carregar_municipios, carregar_trechos,
    construir_grafo, BinarySearchTree, hub_id,
)
from brute_force import (
    forca_bruta_todos_destinos, relatorio_forca_bruta,
    contar_caminhos_por_n,
)
from greedy import (
    dijkstra_completo, prioridade_por_risco,
)
from performance_monitor import rodar_benchmark, analisar_benchmark
from visualizations import (
    plotar_grafo, plotar_bst, plotar_desempenho,
    plotar_tabela_estruturas, plotar_gap_otimalidade,
    plotar_escala_decisao,
)

# ──────────────────────────────────────────────────────────────────────────────
#  CAMINHOS DOS DADOS
# ──────────────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
DATA_RAW = os.path.join(BASE, "data", "raw")

CENARIOS = {
    "rs": {
        "municipios":  os.path.join(DATA_RAW, "municipios_rs.json"),
        "malha":       os.path.join(DATA_RAW, "malha_viaria_rs.json"),
        "usar_tempo":  True,   # peso = tempo (horas)
        "titulo":      "Cenário A — Enchentes RS 2024",
        "descricao":   "Rio Grande do Sul | Hub: Porto Alegre",
    },
    "matopiba": {
        "municipios":  os.path.join(DATA_RAW, "municipios_matopiba.json"),
        "malha":       os.path.join(DATA_RAW, "malha_viaria_matopiba.json"),
        "usar_tempo":  False,  # peso = distância (km)
        "titulo":      "Cenário B — Seca MATOPIBA",
        "descricao":   "MA / TO / PI / BA | Hub: Palmas",
    },
}


# ──────────────────────────────────────────────────────────────────────────────
#  HELPER: separador visual
# ──────────────────────────────────────────────────────────────────────────────
def sep(titulo: str = ""):
    linha = "=" * 65
    if titulo:
        print(f"\n{linha}")
        print(f"  {titulo}")
        print(linha)
    else:
        print(linha)


# ──────────────────────────────────────────────────────────────────────────────
#  PASSO 1 — Carrega e constrói as estruturas para um cenário
# ──────────────────────────────────────────────────────────────────────────────
def carregar_cenario(chave: str) -> dict:
    cfg = CENARIOS[chave]
    municipios = carregar_municipios(cfg["municipios"])
    trechos    = carregar_trechos(cfg["malha"])
    vertices, grafo, meta = construir_grafo(
        municipios, trechos, usar_tempo=cfg["usar_tempo"]
    )

    # BST ordenada por índice de risco
    bst = BinarySearchTree()
    bst.construir(municipios)

    # Hub logístico (ponto de origem)
    hub = hub_id(municipios)

    print(f"\n[✓] {cfg['titulo']} carregado:")
    print(f"    Vértices: {len(vertices)} | Arestas (pares): "
          f"{sum(len(v) for v in grafo.values()) // 2}")
    print(f"    Hub: {vertices[hub][1]} (id={hub})")
    print(f"    Altura da BST: {bst.altura()}")

    return {
        "chave":      chave,
        "cfg":        cfg,
        "municipios": municipios,
        "vertices":   vertices,
        "grafo":      grafo,
        "meta":       meta,
        "bst":        bst,
        "hub":        hub,
    }


# ──────────────────────────────────────────────────────────────────────────────
#  PASSO 2 — Roda Dijkstra e exibe resultado
# ──────────────────────────────────────────────────────────────────────────────
def rodar_dijkstra(cenario: dict) -> dict:
    vertices = cenario["vertices"]
    grafo    = cenario["grafo"]
    hub      = cenario["hub"]
    bst      = cenario["bst"]
    cfg      = cenario["cfg"]

    sep(f"DIJKSTRA — {cfg['titulo']}")

    resultado, ops = dijkstra_completo(grafo, vertices, hub)

    unidade = "h" if cfg["usar_tempo"] else "km"
    print(f"\n{'Destino':<22} {'Custo':>8}  Caminho")
    print("-" * 65)
    for dest_id, info in resultado.items():
        custo   = info["custo"]
        caminho = info["caminho"]
        nomes_caminho = " → ".join(
            vertices[v][1][:8] for v in caminho if v in vertices
        )
        custo_str = f"{custo:.2f}{unidade}" if custo < float("inf") else "∞"
        print(f"{info['nome']:<22} {custo_str:>8}  {nomes_caminho}")

    print(f"\n  Total de arestas relaxadas (ops): {ops}")

    # Priorização por risco (consulta BST)
    priorizados = prioridade_por_risco(resultado, bst, limiar_risco=0.75)
    print(f"\n  Municípios priorizados (risco ≥ 0.75): {len(priorizados)}")
    for p in priorizados[:5]:
        print(f"    {p['nome']:<20} risco={p['risco']:.2f}  "
              f"custo_rota={p['custo_rota']:.2f}{unidade}")

    return resultado


# ──────────────────────────────────────────────────────────────────────────────
#  PASSO 3 — Roda Força Bruta (N ≤ 12) e valida vs Dijkstra
# ──────────────────────────────────────────────────────────────────────────────
def rodar_forca_bruta(cenario: dict, resultado_dij: dict):
    vertices = cenario["vertices"]
    grafo    = cenario["grafo"]
    hub      = cenario["hub"]
    cfg      = cenario["cfg"]
    n        = len(grafo)

    sep(f"FORÇA BRUTA — {cfg['titulo']}")

    if n > 12:
        print(f"\n  N={n} > 12: Força Bruta INVIÁVEL para o cenário completo.")
        print(f"  Rodando apenas nos primeiros 10 nós como demonstração...")

        # Subgrafo com os 10 primeiros nós para demonstração
        ids_sub = list(grafo.keys())[:10]
        hub_sub = hub if hub in ids_sub else ids_sub[0]
        grafo_sub = {k: [(v, p) for v, p in grafo[k] if v in ids_sub]
                     for k in ids_sub}
        vertices_sub = {k: vertices[k] for k in ids_sub if k in vertices}

        resultado_fb = forca_bruta_todos_destinos(
            grafo_sub, vertices_sub, hub_sub
        )
        resultado_dij_sub = {k: resultado_dij[k]
                             for k in ids_sub if k in resultado_dij}
        relatorio_forca_bruta(
            resultado_fb, resultado_dij_sub, vertices_sub, vertices[hub_sub][1]
        )
    else:
        resultado_fb = forca_bruta_todos_destinos(grafo, vertices, hub)
        relatorio_forca_bruta(
            resultado_fb, resultado_dij, vertices, vertices[hub][1]
        )

    return resultado_fb


# ──────────────────────────────────────────────────────────────────────────────
#  PASSO 4 — Explosão combinatória (demonstração)
# ──────────────────────────────────────────────────────────────────────────────
def demonstrar_explosao():
    sep("EXPLOSÃO COMBINATÓRIA — Força Bruta em grafos completos")
    print("\n  (Cada linha: grafo completo com N nós, 0→N-1)\n")
    dados = contar_caminhos_por_n([3, 4, 5, 6, 7, 8, 9, 10])
    return dados


# ──────────────────────────────────────────────────────────────────────────────
#  PASSO 5 — Benchmark de desempenho
# ──────────────────────────────────────────────────────────────────────────────
def rodar_desempenho() -> list:
    sep("BENCHMARK DE DESEMPENHO (N = 5, 8, 10, 12, 20, 50, 100)")
    resultados = rodar_benchmark([5, 8, 10, 12, 20, 50, 100], limite_fb=12)
    analisar_benchmark(resultados)
    return resultados


# ──────────────────────────────────────────────────────────────────────────────
#  PASSO 6 — Gera todas as figuras
# ──────────────────────────────────────────────────────────────────────────────
def gerar_figuras(cenarios_dados: list, benchmark: list):
    sep("GERANDO FIGURAS OBRIGATÓRIAS")

    for dados in cenarios_dados:
        chave    = dados["chave"]
        vertices = dados["vertices"]
        grafo    = dados["grafo"]
        meta     = dados["meta"]
        bst      = dados["bst"]
        hub      = dados["hub"]
        cfg      = dados["cfg"]
        resultado_dij = dados["resultado_dij"]

        # Figura 1 — Grafo geográfico com caminhos Dijkstra
        plotar_grafo(
            grafo, vertices, meta, resultado_dij, hub,
            titulo=cfg["titulo"],
            nome_arquivo=f"fig1_{chave}_grafo.png",
        )

        # Figura 2 — BST de municípios por risco
        plotar_bst(
            bst,
            titulo=f"BST de Municípios por Índice de Risco — {cfg['titulo']}",
            nome_arquivo=f"fig2_{chave}_bst.png",
        )

    # Figura 3 — Comparativo de desempenho
    plotar_desempenho(benchmark, "fig3_desempenho.png")

    # Figura 4 — Tabela de estruturas de dados
    plotar_tabela_estruturas("fig4_tabela_estruturas.png")

    # Figura 5 — Gap de otimalidade e explosão combinatória
    plotar_gap_otimalidade(benchmark, "fig5_gap.png")

    # Figura 6 — Escala de decisão
    plotar_escala_decisao("fig6_escala_decisao.png")

    print(f"\n[✓] Todas as figuras salvas em data/processed/")

# ──────────────────────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 65)
    print("  GLOBAL SOLUTION 2026 — Monitoramento de Riscos Ambientais")
    print("  FIAP | Estruturas de Dados e Algoritmos")
    print("=" * 65)

    cenarios_dados = []

    # ── Roda cada cenário ────────────────────────────────────────────
    for chave in ["rs", "matopiba"]:
        try:
            cenario = carregar_cenario(chave)
            resultado_dij = rodar_dijkstra(cenario)
            cenario["resultado_dij"] = resultado_dij
            rodar_forca_bruta(cenario, resultado_dij)
            cenarios_dados.append(cenario)
        except FileNotFoundError as e:
            print(f"[!] Arquivo não encontrado para cenário '{chave}': {e}")
            continue

    # ── Demonstração explosão combinatória ───────────────────────────
    demonstrar_explosao()

    # ── Benchmark de desempenho ──────────────────────────────────────
    benchmark = rodar_desempenho()

    # ── Figuras ──────────────────────────────────────────────────────
    if cenarios_dados:
        gerar_figuras(cenarios_dados, benchmark)

    sep("CONCLUÍDO")
    print("\n  Figuras → data/processed/")
    print("  Relatório → report/relatorio_final.pdf\n")


if __name__ == "__main__":
    main()
