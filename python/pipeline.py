"""
pipeline.py  –  Análise de Risco de Crédito Híbrido (SRL)
Disciplina: ICC260  |  Prof. Edjard Mota

Fluxo:
  1. Carrega a base relacional Prolog (rede_social.pl)
  2. Extrai features lógicas (grau de risco na rede) via pyswip
  3. Combina com features financeiras clássicas (CSV)
  4. Treina uma Regressão Logística (scikit-learn)
  5. Emite regras probabilísticas estilo ProbLog (XAI)
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

# ── 1. Caminhos ──────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
PROLOG_KB  = os.path.join(BASE_DIR, "..", "prolog", "rede_social.pl")
DATA_CSV   = os.path.join(BASE_DIR, "..", "data",   "dados_financeiros.csv")

PROLOG_AVAILABLE = False

# ── 2. Inicializar motor Prolog ───────────────────────────────
try:
    from pyswip import Prolog
    prolog = Prolog()
    prolog.consult(PROLOG_KB)
    PROLOG_AVAILABLE = True
    print("[OK]  Motor SWI-Prolog conectado via pyswip.")
except ImportError:
    print("[AVISO] pyswip não encontrado – usando fallback Python puro.")
except Exception as e:
    print(f"[AVISO] Erro ao inicializar Prolog: {e}  – usando fallback.")


# ── 3. Fallback: grafo em Python puro ────────────────────────
GRAFO = {
    "joao":    ["ana"],
    "ana":     ["joao", "carlos", "pedro"],
    "carlos":  ["ana", "daniel"],
    "daniel":  [],
    "maria":   ["joao"],
    "pedro":   ["ana", "lucia"],
    "lucia":   ["pedro"],
}
INADIMPLENTES = {"daniel"}

def grau_bfs(origem: str, alvo: str) -> int:
    """BFS para calcular grau mínimo de separação entre dois nós."""
    from collections import deque
    if origem == alvo:
        return 0
    visitados = {origem}
    fila = deque([(origem, 0)])
    while fila:
        no, dist = fila.popleft()
        for vizinho in GRAFO.get(no, []):
            if vizinho == alvo:
                return dist + 1
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append((vizinho, dist + 1))
    return 999  # sem conexão


# ── 4. Feature: grau de risco na rede ────────────────────────
def obter_grau_risco(nome: str) -> int:
    """Retorna o menor grau de conexão com qualquer inadimplente."""
    if PROLOG_AVAILABLE:
        try:
            resultados = list(prolog.query(
                f"risco_conexao({nome.lower()}, daniel, Grau)"
            ))
            if resultados:
                return int(min(r["Grau"] for r in resultados))
            return 999
        except Exception:
            pass  # cai no fallback
    # Fallback Python
    graus = [grau_bfs(nome.lower(), inad) for inad in INADIMPLENTES]
    return min(graus) if graus else 999


# ── 5. Carregar dados e enriquecer com feature relacional ─────
print("\n[1/4] Carregando dados financeiros...")
df = pd.read_csv(DATA_CSV)

print("[2/4] Extraindo features lógicas do grafo social...")
df["grau_risco_rede"] = df["cliente_id"].apply(obter_grau_risco)

print("\n── Dataset Enriquecido ──────────────────────────────────")
print(df.to_string(index=False))


# ── 6. Treinar classificador ──────────────────────────────────
print("\n[3/4] Treinando Regressão Logística...")

features = ["renda_mensal", "score_classico", "grau_risco_rede"]
X = df[features]
y = df["inadimplente_historico"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

modelo = LogisticRegression(max_iter=1000, random_state=42)
modelo.fit(X_scaled, y)

print("\n── Coeficientes Aprendidos ──────────────────────────────")
for feat, coef in zip(features, modelo.coef_[0]):
    sinal = "↑ risco" if coef > 0 else "↓ risco"
    print(f"  {feat:<22}  {coef:+.4f}  ({sinal})")

if len(df) >= 5:
    scores = cross_val_score(modelo, X_scaled, y, cv=3, scoring="accuracy")
    print(f"\n  Acurácia (CV-3): {scores.mean():.2%} ± {scores.std():.2%}")


# ── 7. Inferência + saída estilo ProbLog (XAI) ───────────────
print("\n[4/4] Gerando regras probabilísticas (estilo ProbLog)...")
print("\n── Saída Relacional-Estatística ─────────────────────────")

novos_clientes = [
    {"nome": "joao",    "renda": 5200, "score": 750},
    {"nome": "ana",     "renda": 3100, "score": 610},
    {"nome": "carlos",  "renda": 1800, "score": 420},
    {"nome": "maria",   "renda": 4500, "score": 680},
    {"nome": "pedro",   "renda": 2200, "score": 530},
    {"nome": "lucia",   "renda": 3800, "score": 700},
]

for c in novos_clientes:
    grau = obter_grau_risco(c["nome"])
    x_novo = scaler.transform([[c["renda"], c["score"], grau]])
    prob = modelo.predict_proba(x_novo)[0][1]
    grau_str = str(grau) if grau < 999 else "∞"
    print(f"  {prob:.2f} :: risco({c['nome']}) :- "
          f"conectado_a({c['nome']}, daniel, {grau_str}).")

print("\n[DONE] Pipeline SRL concluído com sucesso.")
