% =============================================================
%  rede_social.pl  –  Base de Conhecimento Relacional
%  Projeto: Análise de Risco de Crédito Híbrido (SRL)
%  Disciplina: ICC260 – Prof. Edjard Mota
% =============================================================

% --- Fatos: transações diretas entre clientes ---
transacao_entre(joao,    ana,    1500).
transacao_entre(ana,     carlos,  800).
transacao_entre(carlos,  daniel,   50).
transacao_entre(maria,   joao,   2200).
transacao_entre(pedro,   ana,     300).
transacao_entre(lucia,   pedro,   750).

% --- Histórico de inadimplência clássico ---
inadimplente(daniel).

% --- Regra: grau de conexão recursivo (bidirecional) ---
% Grau 1 = conexão direta
risco_conexao(X, Y, 1) :-
    transacao_entre(X, Y, _).
risco_conexao(X, Y, 1) :-
    transacao_entre(Y, X, _).

% Grau N = conexão transitiva via intermediário Z
risco_conexao(X, Y, Grau) :-
    transacao_entre(X, Z, _),
    Z \= Y,
    risco_conexao(Z, Y, GrauAnterior),
    Grau is GrauAnterior + 1.

% --- Regra auxiliar: menor grau de conexão ao inadimplente ---
grau_minimo_risco(X, MinGrau) :-
    inadimplente(Alvo),
    aggregate_all(min(G), risco_conexao(X, Alvo, G), MinGrau).

% --- Regra: verificar se há qualquer conexão com inadimplente ---
tem_conexao_risco(X) :-
    inadimplente(Y),
    risco_conexao(X, Y, _).
