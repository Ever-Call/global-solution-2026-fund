"""
data_structures.py
==================
Implementação MANUAL de todas as estruturas de dados do projeto.
Nenhuma biblioteca externa é usada aqui — apenas Python puro.

Estruturas implementadas:
  - Grafo (dicionário de listas de adjacência)
  - Árvore Binária de Busca (BST)
  - Fila de Prioridade (min-heap via heapq)

Autores: [Preencher RA – NOME]
"""

import json
import heapq


# =====================================================================
#  FUNÇÕES DE CARREGAMENTO DOS DADOS JSON
# =====================================================================

def carregar_municipios(caminho: str) -> list:
    """
    Lê o arquivo JSON de municípios e retorna uma lista de dicionários.

    Parâmetro:
      caminho : caminho para o arquivo .json
    """
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    return dados["municipios"]


def carregar_trechos(caminho: str) -> list:
    """
    Lê o arquivo JSON de malha viária e retorna a lista de trechos.

    Parâmetro:
      caminho : caminho para o arquivo .json
    """
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    return dados["trechos"]


# =====================================================================
#  GRAFO — dicionário de listas de adjacência
# =====================================================================

def construir_grafo(municipios: list, trechos: list, usar_tempo: bool = True):
    """
    Constrói o grafo e os metadados a partir dos dados JSON.

    Por que lista de adjacência (e não matriz)?
      - O grafo é ESPARSO (poucas arestas vs. n² possíveis)
      - Espaço: O(V + E) vs. O(V²) da matriz
      - Iterar sobre vizinhos custa O(grau do nó), ótimo para Dijkstra

    Parâmetros:
      municipios : lista de dicts (lida do JSON)
      trechos    : lista de dicts (malha viária)
      usar_tempo : True  → peso = tempo_horas (Cenário RS)
                   False → peso = distancia_km (Cenário MATOPIBA)

    Retorna:
      vertices : dict  {id_ibge → tupla (id, nome, risco, custo, pop)}
      grafo    : dict  {id_ibge → [(vizinho_id, peso), ...]}
      meta     : dict  {id_ibge → {"lat", "lon", "hub", "nome"}}
    """
    # ── Vértices como tuplas imutáveis (formato exigido pelo PDF) ─────
    # tupla = (id_municipio, nome, indice_risco, custo_atendimento, populacao)
    vertices = {}
    meta = {}

    for m in municipios:
        vid = m["id_ibge"]

        # Tupla imutável — o núcleo do vértice no grafo
        vertices[vid] = (
            m["id_ibge"],
            m["nome"],
            m["indice_risco"],
            m["custo_atendimento_mil_reais"],
            m["populacao_ibge_2022"],
        )

        # Metadados extras para visualização (lat/lon) e identificação do hub
        meta[vid] = {
            "lat": m.get("lat", 0.0),
            "lon": m.get("lon", 0.0),
            "hub": m.get("hub", False),
            "nome": m["nome"],
            "estado": m.get("estado", ""),
        }

    # ── Grafo como dicionário de listas de adjacência ─────────────────
    # grafo[u] = [(v1, peso1), (v2, peso2), ...]
    grafo = {vid: [] for vid in vertices}

    for t in trechos:
        u = t["id_origem"]
        v = t["id_destino"]

        # Escolha do peso conforme cenário
        if usar_tempo and "tempo_horas" in t:
            peso = float(t["tempo_horas"])
        else:
            peso = float(t["distancia_km"])

        # Só adiciona aresta se ambos os municípios estão no grafo
        if u in grafo and v in grafo:
            grafo[u].append((v, peso))
            # Grafo não dirigido: aresta nos dois sentidos
            if t.get("bidirecional", True):
                grafo[v].append((u, peso))

    return vertices, grafo, meta


def hub_id(municipios: list) -> int:
    """
    Retorna o id_ibge do município marcado como hub logístico (hub=True).
    O hub é o ponto de origem das equipes de resposta.
    """
    for m in municipios:
        if m.get("hub", False):
            return m["id_ibge"]
    return None


# =====================================================================
#  ÁRVORE BINÁRIA DE BUSCA (BST) — ordenada pelo índice de risco
# =====================================================================

class Node:
    """
    Nó da BST.

    Chave de ordenação: indice_risco (float entre 0.0 e 1.0).

    Propriedade BST:
      Para todo nó n:
        subárvore ESQUERDA → risco < n.risco
        subárvore DIREITA  → risco >= n.risco
    """

    def __init__(self, id_ibge: int, nome: str, risco: float,
                 custo: float, populacao: int):
        self.id_ibge   = id_ibge
        self.nome      = nome
        self.risco     = risco      # ← chave de ordenação
        self.custo     = custo
        self.populacao = populacao
        self.esquerda  = None       # filho com menor risco
        self.direita   = None       # filho com maior risco

    def __repr__(self):
        return f"Node({self.nome}, risco={self.risco:.2f})"


class BinarySearchTree:
    """
    Árvore Binária de Busca de municípios ordenada pelo índice de risco.

    Operações suportadas:
      inserir       → O(h)      — h = altura da árvore
      buscar        → O(h + k)  — k = nós no intervalo
      percurso_in_order → O(n)  — visita todos os nós em ordem
      altura        → O(n)
      remover       → O(h)
    """

    def __init__(self):
        self.raiz = None

    # ── INSERÇÃO ──────────────────────────────────────────────────────
    def inserir(self, id_ibge: int, nome: str, risco: float,
                custo: float, populacao: int):
        """Insere um novo município mantendo a propriedade BST."""
        novo = Node(id_ibge, nome, risco, custo, populacao)
        if self.raiz is None:
            self.raiz = novo
        else:
            self._inserir_rec(self.raiz, novo)

    def _inserir_rec(self, atual: Node, novo: Node):
        """Desce na árvore recursivamente até encontrar o lugar certo."""
        if novo.risco < atual.risco:
            if atual.esquerda is None:
                atual.esquerda = novo      # encaixa à esquerda
            else:
                self._inserir_rec(atual.esquerda, novo)
        else:
            if atual.direita is None:
                atual.direita = novo       # encaixa à direita
            else:
                self._inserir_rec(atual.direita, novo)

    # ── BUSCA POR INTERVALO ───────────────────────────────────────────
    def buscar(self, r_min: float, r_max: float) -> list:
        """
        Retorna lista de Nodes com  r_min <= risco <= r_max.

        Usa podas (pruning) para evitar explorar ramos impossíveis:
          - Não vai à esquerda se todos ali teriam risco < r_min
          - Não vai à direita  se todos ali teriam risco > r_max
        """
        resultado = []
        self._buscar_rec(self.raiz, r_min, r_max, resultado)
        return resultado

    def _buscar_rec(self, no: Node, r_min: float, r_max: float, resultado: list):
        if no is None:
            return
        if no.risco > r_min:            # pode ter candidatos à esquerda
            self._buscar_rec(no.esquerda, r_min, r_max, resultado)
        if r_min <= no.risco <= r_max:  # este nó está no intervalo
            resultado.append(no)
        if no.risco < r_max:            # pode ter candidatos à direita
            self._buscar_rec(no.direita, r_min, r_max, resultado)

    # ── PERCURSO IN-ORDER (ordem crescente de risco) ──────────────────
    def percurso_in_order(self) -> list:
        """
        Retorna lista de Nodes em ordem CRESCENTE de risco.
        Útil para priorizar municípios mais críticos (vem por último).
        """
        resultado = []
        self._in_order_rec(self.raiz, resultado)
        return resultado

    def _in_order_rec(self, no: Node, resultado: list):
        if no is None:
            return
        self._in_order_rec(no.esquerda, resultado)
        resultado.append(no)
        self._in_order_rec(no.direita, resultado)

    # ── ALTURA ────────────────────────────────────────────────────────
    def altura(self) -> int:
        """Calcula a altura da árvore (nível mais profundo)."""
        return self._altura_rec(self.raiz)

    def _altura_rec(self, no: Node) -> int:
        if no is None:
            return 0
        return 1 + max(
            self._altura_rec(no.esquerda),
            self._altura_rec(no.direita)
        )

    # ── REMOÇÃO ───────────────────────────────────────────────────────
    def remover(self, id_ibge: int):
        """
        Remove o nó com o id_ibge indicado.

        Como a BST é ordenada por risco (não por id_ibge), precisamos
        encontrar o nó percorrendo a árvore inteira.
        Após encontrar, aplicamos a remoção padrão de BST:
          - Folha: remove diretamente
          - 1 filho: substitui pelo filho
          - 2 filhos: substitui pelo sucessor in-order (menor da direita)
        """
        self.raiz = self._remover_rec(self.raiz, id_ibge)

    def _remover_rec(self, no: Node, id_ibge: int) -> Node:
        if no is None:
            return None

        if id_ibge == no.id_ibge:
            # ── Nó encontrado ──────────────────────────
            if no.esquerda is None:     # sem filho esquerdo (ou folha)
                return no.direita
            if no.direita is None:      # só tem filho esquerdo
                return no.esquerda
            # Dois filhos: pega o menor da subárvore direita (sucessor)
            suc = self._minimo(no.direita)
            no.id_ibge   = suc.id_ibge
            no.nome      = suc.nome
            no.risco     = suc.risco
            no.custo     = suc.custo
            no.populacao = suc.populacao
            # Remove o sucessor da subárvore direita
            no.direita = self._remover_rec(no.direita, suc.id_ibge)
        else:
            # Como ordenamos por risco e não sabemos o risco deste id,
            # precisamos buscar nos dois lados
            no.esquerda = self._remover_rec(no.esquerda, id_ibge)
            no.direita  = self._remover_rec(no.direita,  id_ibge)

        return no

    def _minimo(self, no: Node) -> Node:
        """Retorna o nó com menor risco em uma subárvore."""
        while no.esquerda is not None:
            no = no.esquerda
        return no

    # ── CONSTRUÇÃO EM LOTE ────────────────────────────────────────────
    def construir(self, municipios: list):
        """Insere todos os municípios da lista de uma vez."""
        for m in municipios:
            self.inserir(
                m["id_ibge"],
                m["nome"],
                m["indice_risco"],
                m["custo_atendimento_mil_reais"],
                m["populacao_ibge_2022"],
            )


# =====================================================================
#  FILA DE PRIORIDADE — wrapper pedagógico sobre heapq
# =====================================================================

class FilaPrioridade:
    """
    Min-heap usando heapq nativo do Python.

    Cada elemento: (prioridade, id_municipio)
    A extração sempre devolve o de MENOR prioridade (menor custo).

    Usado no Dijkstra para extrair o nó não visitado de menor custo.

    Complexidade:
      inserir        → O(log n)
      extrair_minimo → O(log n)
      verificar vazia→ O(1)
    """

    def __init__(self):
        self._heap = []   # list — armazenamento interno

    def inserir(self, prioridade: float, id_municipio):
        """Adiciona (prioridade, id) na fila."""
        heapq.heappush(self._heap, (prioridade, id_municipio))

    def extrair_minimo(self) -> tuple:
        """Remove e retorna o par (prioridade, id) de menor prioridade."""
        return heapq.heappop(self._heap)

    def vazia(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)