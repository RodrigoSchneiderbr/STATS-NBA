import pandas as pd
import numpy as np

df = pd.read_csv("data/jogadores_nba_2026_27_todas_colunas.csv")

column_list = df.columns
print(column_list)

df = df.rename(columns={
    'PLAYER_ID': 'id_jogador',
    'PLAYER_NAME': 'nome_jogador',
    'NICKNAME': 'apelido',
    'TEAM_ID': 'id_time',
    'TEAM_ABBREVIATION': 'sigla_time',
    'AGE': 'idade',
    'GP': 'jogos_disputados',
    'W': 'vitorias',
    'L': 'derrotas',
    'W_PCT': 'aproveitamento_vitorias',
    'MIN': 'minutos',
    'FGM': 'arremessos_convertidos',
    'FGA': 'arremessos_tentados',
    'FG_PCT': 'aproveitamento_arremessos',
    'FG3M': 'cestas_3_convertidas',
    'FG3A': 'cestas_3_tentadas',
    'FG3_PCT': 'aproveitamento_3_pontos',
    'FTM': 'lances_livres_convertidos',
    'FTA': 'lances_livres_tentados',
    'FT_PCT': 'aproveitamento_lances_livres',
    'OREB': 'rebotes_ofensivos',
    'DREB': 'rebotes_defensivos',
    'REB': 'rebotes_totais',
    'AST': 'assistencias',
    'TOV': 'turnovers',
    'STL': 'roubos_bola',
    'BLK': 'tocos',
    'BLKA': 'tocos_sofridos',
    'PF': 'faltas_pessoais',
    'PFD': 'faltas_sofridas',
    'PTS': 'pontos',
    'PLUS_MINUS': 'mais_menos',
    'NBA_FANTASY_PTS': 'pontos_fantasy',
    'DD2': 'double_doubles',
    'TD3': 'triple_doubles',
    'WNBA_FANTASY_PTS': 'pontos_fantasy_wnba',
    'FP_HIGH_SCORE': 'maior_pontuacao_fantasy',
    'GP_RANK': 'rank_jogos',
    'W_RANK': 'rank_vitorias',
    'L_RANK': 'rank_derrotas',
    'W_PCT_RANK': 'rank_aproveitamento_vitorias',
    'MIN_RANK': 'rank_minutos',
    'FGM_RANK': 'rank_arremessos_convertidos',
    'FGA_RANK': 'rank_arremessos_tentados',
    'FG_PCT_RANK': 'rank_aproveitamento_arremessos',
    'FG3M_RANK': 'rank_cestas_3_convertidas',
    'FG3A_RANK': 'rank_cestas_3_tentadas',
    'FG3_PCT_RANK': 'rank_aproveitamento_3_pontos',
    'FTM_RANK': 'rank_lances_livres_convertidos',
    'FTA_RANK': 'rank_lances_livres_tentados',
    'FT_PCT_RANK': 'rank_aproveitamento_lances_livres',
    'OREB_RANK': 'rank_rebotes_ofensivos',
    'DREB_RANK': 'rank_rebotes_defensivos',
    'REB_RANK': 'rank_rebotes_totais',
    'AST_RANK': 'rank_assistencias',
    'TOV_RANK': 'rank_turnovers',
    'STL_RANK': 'rank_roubos_bola',
    'BLK_RANK': 'rank_tocos',
    'BLKA_RANK': 'rank_tocos_sofridos',
    'PF_RANK': 'rank_faltas_pessoais',
    'PFD_RANK': 'rank_faltas_sofridas',
    'PTS_RANK': 'rank_pontos',
    'PLUS_MINUS_RANK': 'rank_mais_menos',
    'NBA_FANTASY_PTS_RANK': 'rank_pontos_fantasy',
    'DD2_RANK': 'rank_double_doubles',
    'TD3_RANK': 'rank_triple_doubles',
    'WNBA_FANTASY_PTS_RANK': 'rank_pontos_fantasy_wnba',
    'FP_HIGH_SCORE_RANK': 'rank_maior_pontuacao_fantasy',
    'TEAM_COUNT': 'total_times'
})

colunas_para_remover = [
    'pontos_fantasy', 
    'pontos_fantasy_wnba', 
    'maior_pontuacao_fantasy',
    'rank_pontos_fantasy', 
    'rank_pontos_fantasy_wnba', 
    'rank_maior_pontuacao_fantasy'
]

df = df.drop(columns=colunas_para_remover, errors='ignore')

colunas_rank = [
    'rank_jogos', 'rank_vitorias', 'rank_derrotas', 'rank_aproveitamento_vitorias',
    'rank_minutos', 'rank_arremessos_convertidos', 'rank_arremessos_tentados',
    'rank_aproveitamento_arremessos', 'rank_cestas_3_convertidas', 'rank_cestas_3_tentadas',
    'rank_aproveitamento_3_pontos', 'rank_lances_livres_convertidos', 'rank_lances_livres_tentados',
    'rank_aproveitamento_lances_livres', 'rank_rebotes_ofensivos', 'rank_rebotes_defensivos',
    'rank_rebotes_totais', 'rank_assistencias', 'rank_turnovers', 'rank_roubos_bola',
    'rank_tocos', 'rank_tocos_sofridos', 'rank_faltas_pessoais', 'rank_faltas_sofridas',
    'rank_pontos', 'rank_mais_menos', 'rank_pontos_fantasy', 'rank_double_doubles',
    'rank_triple_doubles', 'rank_pontos_fantasy_wnba', 'rank_maior_pontuacao_fantasy'
]

df = df.drop(columns=colunas_rank, errors='ignore')

#INDICE PELADEIRO MASTER
df = df.fillna(0)

# Criar as métricas por Jogo
df['fg3_tentadas_por_jogo'] = np.where(df['jogos_disputados'] > 0, df['cestas_3_tentadas'] / df['jogos_disputados'], 0)

 #O CÁLCULO DO PELADEIRO MASTER ATUALIZADO
df_peladeiro = df.copy()

# A) Punição por baixa conversão de 3 (Volume x Ineficiência ao quadrado)
ineficiencia_3pt = 1 - df_peladeiro['aproveitamento_3_pontos']
fator_chute_errado = df_peladeiro['fg3_tentadas_por_jogo'] * (ineficiencia_3pt ** 2)

# B) Defesa Fraca (Usando 'turnovers', 'tocos' e 'faltas')
defesa_fraca = (1 / (df_peladeiro['turnovers'] + 1)) * (1 / (df_peladeiro['tocos_sofridos'] + 1)) * (df_peladeiro['faltas_pessoais'] + 1)

# C) Queda de Pontos do Time (PLUS_MINUS negativo indica prejuízo em quadra)
estrago_no_placar = np.where(df_peladeiro['mais_menos'] < 0, abs(df_peladeiro['mais_menos']), 0)

# D) Índice Final do Peladeiro Master
df_peladeiro['peladeiro_master_index'] = (
    (fator_chute_errado * 0.4) +
    (np.log1p(defesa_fraca) * 0.2) +
    (estrago_no_placar * 0.4)
)

# Filtramos apenas jogadores que tentam pelo menos 2 bolas de 3 por jogo
df_peladeiro = df_peladeiro[df_peladeiro['fg3_tentadas_por_jogo'] >= 2]

# Exibir o Top 10 Oficial dos Reis do Tijolo e Anti-Defesa
top_peladeiros = df_peladeiro.sort_values(by='peladeiro_master_index', ascending=False).head(10)

## Melhores defensores do times

df_defesa = df.copy()

# 1. Limpar eventuais valores nulos para evitar erros matemáticos
df_defesa = df_defesa.fillna(0)

# 2. Criar as métricas por Jogo (Médias por partida para justa comparação)
df_defesa['minutos_por_jogo'] = np.where(df_defesa['jogos_disputados'] > 0, df_defesa['minutos'] / df_defesa['jogos_disputados'], 0)
df_defesa['roubos_por_jogo'] = np.where(df_defesa['jogos_disputados'] > 0, df_defesa['roubos_bola'] / df_defesa['jogos_disputados'], 0)
df_defesa['tocos_por_jogo'] = np.where(df_defesa['jogos_disputados'] > 0, df_defesa['tocos'] / df_defesa['jogos_disputados'], 0)
df_defesa['rebotes_def_por_jogo'] = np.where(df_defesa['jogos_disputados'] > 0, df_defesa['rebotes_defensivos'] / df_defesa['jogos_disputados'], 0)

# 3. CÁLCULO DO ÍNDICE DE DEFENSOR ELITE COM CLASSIFICAÇÃO DO TIME

# A) Atividade Pura (Roubos + Tocos pesam forte)
atividade_pura = (df_defesa['roubos_por_jogo'] * 0.35) + (df_defesa['tocos_por_jogo'] * 0.35)

# B) O Rebote Defensivo atenuando o impacto (desconto proporcional)
fator_atenuacao_rebote = df_defesa['rebotes_def_por_jogo'] * 0.15

# C) Impacto Positivo no Saldo de Pontos do Time (PLUS_MINUS positivo)
impacto_positivo_placar = np.where(df_defesa['mais_menos'] > 0, df_defesa['mais_menos'], 0)
impacto_normalizado = impacto_positivo_placar / 10

# D) Classificação / Aproveitamento do Time (Multiplicador de Sucesso Coletivo)
# Se o time tem um aproveitamento alto (ex: 0.700), o índice ganha tração; se for muito baixo, o valor é atenuado.
fator_sucesso_time = df_defesa['aproveitamento_vitorias']

# E) Fator Disciplina (penaliza excesso de faltas por jogo)
fator_disciplina = (df_defesa['faltas_pessoais'] / df_defesa['jogos_disputados']) + 1

# F) Fórmula Final (Integrando a defesa ativa, saldo do time, penalidade de rebote passivo e o sucesso da equipe)
df_defesa['defensor_elite_index'] = (
    ((atividade_pura - fator_atenuacao_rebote) + (impacto_normalizado * 0.3))
    * (1 + fator_sucesso_time) # Multiplica pelo bônus do aproveitamento do time
) / fator_disciplina

# Filtro de minutagem: mínimo de 15 minutos por jogo
df_defesa_filtrado = df_defesa[df_defesa['minutos_por_jogo'] >= 15]

# Exibir o Top 10 dos Melhores Defensores considerando a campanha da equipe
top_defensores = df_defesa_filtrado.sort_values(by='defensor_elite_index', ascending=False).head(10)

print(top_defensores[[
    'nome_jogador', 'sigla_time', 'jogos_disputados',
    'aproveitamento_vitorias', 'roubos_por_jogo', 'tocos_por_jogo',
    'mais_menos', 'defensor_elite_index'
]])

## time ideal e MVP

df_ideal = df.copy()

# 1. Limpar valores nulos para evitar erros
df_ideal = df_ideal.fillna(0)

# 2. Criar métricas por Jogo (Médias por partida para justa comparação)
df_ideal['minutos_por_jogo'] = np.where(df_ideal['jogos_disputados'] > 0, df_ideal['minutos'] / df_ideal['jogos_disputados'], 0)
df_ideal['pontos_por_jogo'] = np.where(df_ideal['jogos_disputados'] > 0, df_ideal['pontos'] / df_ideal['jogos_disputados'], 0)
df_ideal['rebotes_por_jogo'] = np.where(df_ideal['jogos_disputados'] > 0, df_ideal['rebotes_totais'] / df_ideal['jogos_disputados'], 0)
df_ideal['assistencias_por_jogo'] = np.where(df_ideal['jogos_disputados'] > 0, df_ideal['assistencias'] / df_ideal['jogos_disputados'], 0)

# 3. FILTRO DE PLAYOFF / ALTO DESEMPENHO COLETIVO (Aproveitamento >= 50%)
df_playoffs = df_ideal[df_ideal['aproveitamento_vitorias'] >= 0.50].copy()

# 4. CÁLCULO DO ÍNDICE "ALL-NBA TEAM" COM PLUS DE TRIPLO-DUPLO

# A) Bloco de Estatísticas Brutas por Jogo (Pontos, Rebotes Totais e Assistências)
estatisticas_gerais = (
    (df_playoffs['pontos_por_jogo'] * 0.4) + 
    (df_playoffs['rebotes_por_jogo'] * 0.3) + 
    (df_playoffs['assistencias_por_jogo'] * 0.3)
)

# B) Impacto Positivo no Saldo de Pontos do Time (PLUS_MINUS positivo normalizado)
impacto_positivo = np.where(df_playoffs['mais_menos'] > 0, df_playoffs['mais_menos'], 0)
impacto_normalizado = impacto_positivo / 10

# C) O PLUS DE TRIPLO-DUPLO (Multiplicador de versatilidade)
# Quanto mais triplo-duplos o jogador acumula na temporada, maior o bônus percentual aplicado ao score dele
bonus_triplo_duplo = 1 + (df_playoffs['triple_doubles'] * 0.1)  # Bônus de 2% por triplo-duplo acumulado

# D) Índice Final All-NBA com o Plus
df_playoffs['all_nba_index'] = (
    ((estatisticas_gerais * 0.7) + (impacto_normalizado * 0.3)) 
    * bonus_triplo_duplo
)

# 5. FILTROS DE ELEGIBILIDADADE (Minutagem mínima de 25 min por jogo)
df_elegivel = df_playoffs[df_playoffs['minutos_por_jogo'] >= 30]

# Exibir o Top 15 da Liga (Equivalente aos 3 Times All-NBA)
top_all_nba = df_elegivel.sort_values(by='all_nba_index', ascending=False).head(15)

print(top_all_nba[[
    'nome_jogador', 'sigla_time', 'jogos_disputados', 
    'aproveitamento_vitorias', 'pontos_por_jogo', 
    'rebotes_por_jogo', 'assistencias_por_jogo', 
    'triple_doubles', 'mais_menos', 'all_nba_index'
]])