# Análise de Risco de Crédito Híbrido (SRL)

> ICC260 – Inteligência Artificial | Prof. Edjard Mota | UFAM

Sistema de **Statistical Relational Learning** que combina SWI-Prolog (grafo social) com Python/scikit-learn (Regressão Logística) para análise de risco de crédito com saídas explicáveis estilo ProbLog.

## Início Rápido

```bash
# 1. Clonar
git clone https://github.com/<seu-usuario>/credit-risk-srl.git
cd credit-risk-srl

# 2. Instalar dependências
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Executar
python python/pipeline.py
```

Consulte o **[HOWTO.md](HOWTO.md)** para instruções completas de instalação, execução e interpretação dos resultados.

## Tecnologias
- SWI-Prolog 8.4+ (base relacional e inferência recursiva)
- pyswip (ponte Python ↔ Prolog)
- pandas + scikit-learn (pipeline ML)
- ProbLog-style output (XAI)
