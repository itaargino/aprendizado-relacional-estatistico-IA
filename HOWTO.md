# How-To: Análise de Risco de Crédito Híbrido (SRL)
**Disciplina ICC260 – Prof. Edjard Mota**  
*Statistical Relational Learning com SWI-Prolog + Python*

---

## Índice
1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Estrutura do Repositório](#2-estrutura-do-repositório)
3. [Pré-Requisitos](#3-pré-requisitos)
4. [Instalação e Configuração](#4-instalação-e-configuração)
5. [Execução Passo a Passo](#5-execução-passo-a-passo)
6. [Resultado Esperado](#6-resultado-esperado)
7. [Entendendo as Saídas](#7-entendendo-as-saídas)
8. [Modo Fallback (sem SWI-Prolog)](#8-modo-fallback-sem-swi-prolog)
9. [Rubrica e Critérios](#9-rubrica-e-critérios)

---

## 1. Visão Geral do Projeto

Este projeto implementa um sistema híbrido de **Statistical Relational Learning (SRL)** que une:

| Componente | Tecnologia | Responsabilidade |
|---|---|---|
| Base Relacional | SWI-Prolog | Modelar grafo social de transações, calcular grau de conexão recursivo com inadimplentes |
| Ponte | pyswip | Consultar o motor Prolog dinamicamente a partir do Python |
| Classificador | scikit-learn | Treinar Regressão Logística com features clássicas + relacionais |
| Saída XAI | ProbLog-style | Emitir regras probabilísticas explicáveis |


## 2. Estrutura do Repositório

```
credit-risk-srl/
├── prolog/
│   └── rede_social.pl        # Base de conhecimento: grafo + regras recursivas
├── python/
│   └── pipeline.py           # Extração de features + treinamento + inferência XAI
├── data/
│   └── dados_financeiros.csv # Dataset financeiro dos clientes
├── requirements.txt          # Dependências Python
├── HOWTO.md                  # Este documento
└── README.md                 # Visão geral rápida
```

---

## 3. Pré-Requisito

| Software | Versão Mínima | Verificar com |
|---|---|---|
| Python | 3.9+ | `python3 --version` |
| pip | 22+ | `pip3 --version` |
| SWI-Prolog | 8.4+ | `swipl --version` |
| Git | qualquer | `git --version` |

> **Nota:** O SWI-Prolog é **opcional** – o script possui fallback em Python puro (BFS).  
> Para a avaliação completa instale-o.

---

## 4. Instalação e Configuração

### Passo 4.1 – Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/credit-risk-srl.git
cd credit-risk-srl
```

### Passo 4.2 – Instalar SWI-Prolog

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install swi-prolog -y
# Verificar:
swipl --version
```

**macOS (Homebrew):**
```bash
brew install swi-prolog
```

### Passo 4.3 – Criar ambiente virtual Python

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
```

### Passo 4.4 – Instalar dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> A biblioteca `pyswip` é o conector Python ↔ SWI-Prolog.  
> Ela exige que `swipl` esteja no PATH do sistema.

---

## 5. Execução Passo a Passo

### 5.1 – Testar a base Prolog isoladamente

```bash
swipl prolog/rede_social.pl
```

No prompt do Prolog (`?-`), teste as consultas:

```prolog
% Grau de conexão de joao com daniel
?- risco_conexao(joao, daniel, Grau).

% Todos os graus possíveis
?- findall(X-G, risco_conexao(X, daniel, G), Pares).

% Sair
?- halt.
```

**Saída esperada:**
```
Grau = 3 ;    % joao → ana → carlos → daniel
Grau = 3 .
```

### 5.2 – Executar o pipeline completo

```bash
# A partir da raiz do projeto, com o venv ativado:
python python/pipeline.py
```

---

## 6. Resultado Esperado

Ao executar `python python/pipeline.py`, a saída no terminal será:

```
[OK]  Motor SWI-Prolog conectado via pyswip.

[1/4] Carregando dados financeiros...
[2/4] Extraindo features lógicas do grafo social...

── Dataset Enriquecido ──────────────────────────────────
 cliente_id  renda_mensal  score_classico  inadimplente_historico  grau_risco_rede
       joao          5200             750                       0                3
        ana          3100             610                       0                2
     carlos          1800             420                       1                1
      maria          4500             680                       0                4
      pedro          2200             530                       1                3
      lucia          3800             700                       0                4
    roberto          1500             380                       1              999
    fernanda         6000             820                       0              999

[3/4] Treinando Regressão Logística...

── Coeficientes Aprendidos ──────────────────────────────
  renda_mensal            -0.8312  (↓ risco)
  score_classico          -1.2045  (↓ risco)
  grau_risco_rede         +0.3871  (↑ risco)

  Acurácia (CV-3): 75.00% ± 12.50%

[4/4] Gerando regras probabilísticas (estilo ProbLog)...

── Saída Relacional-Estatística ─────────────────────────
  0.18 :: risco(joao)   :- conectado_a(joao,   daniel, 3).
  0.31 :: risco(ana)    :- conectado_a(ana,    daniel, 2).
  0.78 :: risco(carlos) :- conectado_a(carlos, daniel, 1).
  0.22 :: risco(maria)  :- conectado_a(maria,  daniel, 4).
  0.65 :: risco(pedro)  :- conectado_a(pedro,  daniel, 3).
  0.15 :: risco(lucia)  :- conectado_a(lucia,  daniel, 4).

[DONE] Pipeline SRL concluído com sucesso.
```

> Os valores numéricos exatos podem variar conforme os dados de treino.

---

## 7. Entendendo as Saídas

### 7.1 – Coluna `grau_risco_rede`

| Valor | Interpretação |
|---|---|
| `1` | Transação direta com inadimplente |
| `2` | Um intermediário (amigo de inadimplente) |
| `3` | Dois intermediários |
| `999` | Sem conexão no grafo |

### 7.2 – Coeficientes da Regressão Logística

- **Negativo** → feature **reduz** a probabilidade de inadimplência (ex: renda alta = menos risco)
- **Positivo** → feature **aumenta** a probabilidade (ex: grau baixo com inadimplente = mais risco)

### 7.3 – Regras ProbLog-style

```
0.78 :: risco(carlos) :- conectado_a(carlos, daniel, 1).
```
Lê-se: *"Existe 78% de probabilidade de carlos ser inadimplente,  
dado que ele transacionou diretamente com daniel (grau 1)."*

Esta representação é a essência do **SRL**: combina lógica estruturada (Prolog) com calibração estatística (Regressão Logística), produzindo saídas **interpretáveis** (XAI).

---

## 8. Modo Fallback (sem SWI-Prolog)

Se o SWI-Prolog não estiver instalado, o script detecta automaticamente e usa uma implementação BFS em Python puro para calcular o grau de distância no grafo. O resultado numérico é idêntico.

```
[AVISO] pyswip não encontrado – usando fallback Python puro.
```

O pipeline continua normalmente, mas a consulta relacional não utiliza o motor Prolog.

---

## 9. Rubrica e Critérios

| Critério | Peso | O que será avaliado |
|---|---|---|
| **Implementação Lógica** | 30% | `rede_social.pl`: recursão correta dos graus, fatos bem modelados, regras relacionais |
| **Ponte e Pipeline** | 40% | `pipeline.py`: uso correto do pyswip, integração Pandas, treinamento via Scikit-Learn sem erros |
| **Análise Crítica / XAI** | 30% | Discussão de como as regras probabilísticas produzem IA explicável, justa e auditável |