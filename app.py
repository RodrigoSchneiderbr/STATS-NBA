import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path
import time

# ==========================================
# 1. CONFIGURAÇÃO DE CAMINHOS RELATIVOS (Portátil)
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FILENAME = DATA_DIR / "jogadores_nba_2026_27_todas_colunas.csv"

# Garante que a pasta data/ existe na raiz do projeto
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Analítico NBA 2026-27",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Dashboard Analítico da NBA (Temporada 2026-27)")
st.markdown("Análise estatística avançada baseada nas estatísticas consolidadas da temporada.")

# ==========================================
# 3. BOTÃO DE PRIMEIRA EXECUÇÃO (Caso o CSV não exista)
# ==========================================
if not FILENAME.exists():
    st.warning("⚠️ O arquivo de dados consolidados ainda não foi gerado.")
    st.info("Esta é a primeira execução. Clique no botão abaixo para baixar os dados da API da NBA diretamente por aqui.")
    
    if st.button("🚀 Gerar Base de Dados da Temporada (Primeira Execução)", type="primary"):
        with st.spinner("Buscando estatísticas oficiais da NBA... Isso pode levar alguns segundos."):
            try:
                # Importa a biblioteca diretamente no Streamlit
                from nba_api.stats.endpoints import leaguedashplayerstats
                
                # Configura pandas
                pd.set_option('display.max_columns', None)
                
                # Puxa os dados da API
                player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                    season='2026-27',
                    timeout=60
                )
                df_players = player_stats.get_data_frames()[0]
                
                # Salva o arquivo CSV no caminho relativo correto
                df_players.to_csv(FILENAME, index=False)
                
                # Pausa de segurança para gravação no disco
                time.sleep(1)
                
                if FILENAME.exists():
                    st.success("✅ Base de dados gerada com sucesso! Recarregando a aplicação...")
                    st.rerun()
                else:
                    st.error("❌ Ocorreu um erro ao gravar o arquivo CSV no disco.")
                    
            except ImportError:
                st.error("❌ A biblioteca `nba_api` não está instalada neste ambiente. Rode `pip install nba_api` no seu terminal uma única vez.")
            except Exception as e:
                st.error(f"❌ Erro ao conectar com a API da NBA: {e}")
        st.stop()
        
time.sleep(20)  # Pausa de segurança para evitar sobrecarga na API

# ==========================================
# 4. CARREGAMENTO E PADRONIZAÇÃO DOS DADOS
# ==========================================
@st.cache_data
def carregar_e_padronizar_dados(caminho):
    if not os.path.exists(caminho):
        return None
    
    df = pd.read_csv(caminho)
    df = df.fillna(0)
    
    renomear_colunas = {
        'PLAYER_NAME': 'nome_jogador',
        'TEAM_ABBREVIATION': 'sigla_time',
        'GP': 'jogos_disputados',
        'W': 'vitorias',
        'L': 'derrotas',
        'MIN': 'minutos',
        'PTS': 'pontos',
        'REB': 'rebotes_totais',
        'DREB': 'rebotes_defensivos',
        'AST': 'assistencias',
        'STL': 'roubos_bola',
        'BLK': 'tocos',
        'TOV': 'turnovers',
        'PF': 'faltas_pessoais',
        'PLUS_MINUS': 'mais_menos',
        'FG3A': 'cestas_3_tentadas',
        'FG3_PCT': 'aproveitamento_3_pontos'
    }
    
    df = df.rename(columns={k: v for k, v in renomear_colunas.items() if k in df.columns})
    return df

df_jogadores = carregar_e_padronizar_dados(FILENAME)

if df_jogadores is None:
    st.error(f"⚠️ O arquivo de dados ainda não está disponível.")
else:
    # Abas para separar as análises
    aba1, aba2, aba3 = st.tabs(["🔥 Peladeiro Master", "🛡️ Defensor Elite", "⭐ All-NBA Teams"])
    
    def extrair_coluna(df, nomes_possiveis, valor_padrao=0.0):
        for nome in nomes_possiveis:
            if nome in df.columns:
                return pd.to_numeric(df[nome], errors='coerce').fillna(valor_padrao)
        return pd.Series(valor_padrao, index=df.index)

    # ==========================================
    # ABA 1: PELADEIRO MASTER
    # ==========================================
    with aba1:
        st.subheader("Top 10 — Peladeiro Master (Os Reis do Tijolo e Anti-Defesa)")
        st.markdown("Métrica focada em ineficiência de 3 pontos, desperdícios/faltas e prejuízo no saldo de pontos do time.")
        
        df_pel = df_jogadores.copy()
        
        jogos = extrair_coluna(df_pel, ['jogos_disputados', 'GP'], 1.0)
        cestas_3_tentadas = extrair_coluna(df_pel, ['cestas_3_tentadas', 'FG3A', 'arremessos_3_tentados'], 0.0)
        aprov_3pt_raw = extrair_coluna(df_pel, ['aproveitamento_3_pontos', 'FG3_PCT'], 0.3)
        turnovers = extrair_coluna(df_pel, ['turnovers', 'TOV'], 0.0)
        tocos_sofridos = extrair_coluna(df_pel, ['tocos_sofridos', 'BLK_AGAINST'], 0.0)
        faltas_pessoais = extrair_coluna(df_pel, ['faltas_pessoais', 'PF'], 0.0)
        mais_menos = extrair_coluna(df_pel, ['mais_menos', 'PLUS_MINUS'], 0.0)
        roubos_bola = extrair_coluna(df_pel, ['roubos_bola', 'STL'], 0.0)

        aproveitamento_3_pontos = np.where(aprov_3pt_raw > 1.0, aprov_3pt_raw / 100.0, aprov_3pt_raw)

        df_pel['jogos_disputados'] = jogos
        df_pel['fg3_tentadas_por_jogo'] = np.where(jogos > 0, cestas_3_tentadas / jogos, 0)
        df_pel['aproveitamento_3_pontos'] = aproveitamento_3_pontos

        ineficiencia_3pt = 1 - df_pel['aproveitamento_3_pontos']
        fator_chute_errado = df_pel['fg3_tentadas_por_jogo'] * (ineficiencia_3pt ** 2)
        defesa_fraca = (1 / (turnovers + 1)) * (1 / (tocos_sofridos + 1)) * (faltas_pessoais + 1)
        estrago_no_placar = np.where(mais_menos < 0, abs(mais_menos), 0)

        df_pel['peladeiro_master_index'] = (
            (fator_chute_errado * 0.4) + 
            (np.log1p(defesa_fraca) * 0.2) + 
            (estrago_no_placar * 0.4)
        )

        df_peladeiro_filtrado = df_pel[df_pel['fg3_tentadas_por_jogo'] >= 2]
        top_peladeiros = df_peladeiro_filtrado.sort_values(by='peladeiro_master_index', ascending=False).head(10)

        if 'nome_jogador' not in top_peladeiros.columns and 'PLAYER_NAME' in top_peladeiros.columns:
            top_peladeiros['nome_jogador'] = top_peladeiros['PLAYER_NAME']
        if 'sigla_time' not in top_peladeiros.columns and 'TEAM_ABBREVIATION' in top_peladeiros.columns:
            top_peladeiros['sigla_time'] = top_peladeiros['TEAM_ABBREVIATION']
        top_peladeiros['roubos_bola'] = roubos_bola.loc[top_peladeiros.index]

        colunas_exibir = [
            'nome_jogador', 'sigla_time', 'jogos_disputados',
            'fg3_tentadas_por_jogo', 'aproveitamento_3_pontos',
            'roubos_bola', 'mais_menos', 'peladeiro_master_index'
        ]
        colunas_disponiveis = [c for c in colunas_exibir if c in top_peladeiros.columns]

        st.dataframe(top_peladeiros[colunas_disponiveis].reset_index(drop=True), use_container_width=True)

    # ==========================================
    # ABA 2: DEFENSOR ELITE
    # ==========================================
    with aba2:
        st.subheader("Top 10 — Defensores Elite (Cães de Guarda da Quadra)")
        st.markdown("Foco em desarmes, tocos, tábua defensiva atenuada, impacto positivo e disciplina.")
        
        df_def = df_jogadores.copy()
        
        jogos = extrair_coluna(df_def, ['jogos_disputados', 'GP'], 1.0)
        minutos = extrair_coluna(df_def, ['minutos', 'MIN'], 0.0)
        roubos = extrair_coluna(df_def, ['roubos_bola', 'STL'], 0.0)
        tocos = extrair_coluna(df_def, ['tocos', 'BLK'], 0.0)
        dreb = extrair_coluna(df_def, ['rebotes_defensivos', 'DREB'], 0.0)
        mais_menos = extrair_coluna(df_def, ['mais_menos', 'PLUS_MINUS'], 0.0)
        faltas = extrair_coluna(df_def, ['faltas_pessoais', 'PF'], 0.0)
        
        vitorias = extrair_coluna(df_def, ['vitorias', 'W'], 0.0)
        derrotas = extrair_coluna(df_def, ['derrotas', 'L'], 0.0)
        total_partidas_jogador = vitorias + derrotas
        aprov_raw = extrair_coluna(df_def, ['aproveitamento_vitorias'], 0.0)
        
        fator_sucesso_time = np.where(
            total_partidas_jogador > 0,
            vitorias / total_partidas_jogador,
            np.where(aprov_raw > 1.0, aprov_raw / 100.0, aprov_raw)
        )

        df_def['minutos_por_jogo'] = np.where(jogos > 0, minutos / jogos, 0)
        df_def['roubos_por_jogo'] = np.where(jogos > 0, roubos / jogos, 0)
        df_def['tocos_por_jogo'] = np.where(jogos > 0, tocos / jogos, 0)
        df_def['rebotes_def_por_jogo'] = np.where(jogos > 0, dreb / jogos, 0)
        df_def['aproveitamento_vitorias'] = fator_sucesso_time

        atividade_pura = (df_def['roubos_por_jogo'] * 0.35) + (df_def['tocos_por_jogo'] * 0.35)
        fator_atenuacao_rebote = df_def['rebotes_def_por_jogo'] * 0.15
        impacto_positivo_placar = np.where(mais_menos > 0, mais_menos, 0)
        impacto_normalizado = impacto_positivo_placar / 10
        fator_disciplina = (faltas / jogos) + 1

        df_def['defensor_elite_index'] = (
            ((atividade_pura - fator_atenuacao_rebote) + (impacto_normalizado * 0.3))
            * (1 + fator_sucesso_time)
        ) / fator_disciplina

        df_def_filtrado = df_def[df_def['minutos_por_jogo'] >= 15]
        top_defensores = df_def_filtrado.sort_values(by='defensor_elite_index', ascending=False).head(10)

        if 'nome_jogador' not in top_defensores.columns and 'PLAYER_NAME' in top_defensores.columns:
            top_defensores['nome_jogador'] = top_defensores['PLAYER_NAME']
        if 'sigla_time' not in top_defensores.columns and 'TEAM_ABBREVIATION' in top_defensores.columns:
            top_defensores['sigla_time'] = top_defensores['TEAM_ABBREVIATION']

        colunas_exibir = [
            'nome_jogador', 'sigla_time', 'jogos_disputados',
            'aproveitamento_vitorias', 'roubos_por_jogo', 'tocos_por_jogo',
            'mais_menos', 'defensor_elite_index'
        ]
        colunas_disponiveis = [c for c in colunas_exibir if c in top_defensores.columns]

        st.dataframe(top_defensores[colunas_disponiveis].reset_index(drop=True), use_container_width=True)

    # ==========================================
    # ABA 3: ALL-NBA TEAMS
    # ==========================================
    with aba3:
        st.subheader("Top 15 — All-NBA Teams (Os Craques Completos)")
        st.markdown("Equilíbrio geral de pontuação, rebotes, assistências, saldo positivo e bônus de triplo-duplo.")
        
        df_ideal = df_jogadores.copy()
        
        jogos = extrair_coluna(df_ideal, ['jogos_disputados', 'GP'], 1.0)
        minutos = extrair_coluna(df_ideal, ['minutos', 'MIN'], 0.0)
        pontos = extrair_coluna(df_ideal, ['pontos', 'PTS'], 0.0)
        rebotes = extrair_coluna(df_ideal, ['rebotes_totais', 'REB'], 0.0)
        assistencias = extrair_coluna(df_ideal, ['assistencias', 'AST'], 0.0)
        mais_menos = extrair_coluna(df_ideal, ['mais_menos', 'PLUS_MINUS'], 0.0)
        triple_doubles = extrair_coluna(df_ideal, ['triple_doubles'], 0.0)
        
        vitorias = extrair_coluna(df_ideal, ['vitorias', 'W'], 0.0)
        derrotas = extrair_coluna(df_ideal, ['derrotas', 'L'], 0.0)
        total_partidas_jogador = vitorias + derrotas
        aprov_raw = extrair_coluna(df_ideal, ['aproveitamento_vitorias'], 0.0)
        
        aprov_vitorias = np.where(
            total_partidas_jogador > 0,
            vitorias / total_partidas_jogador,
            np.where(aprov_raw > 1.0, aprov_raw / 100.0, aprov_raw)
        )

        df_ideal['minutos_por_jogo'] = np.where(jogos > 0, minutos / jogos, 0)
        df_ideal['pontos_por_jogo'] = np.where(jogos > 0, pontos / jogos, 0)
        df_ideal['rebotes_por_jogo'] = np.where(jogos > 0, rebotes / jogos, 0)
        df_ideal['assistencias_por_jogo'] = np.where(jogos > 0, assistencias / jogos, 0)
        df_ideal['aproveitamento_vitorias'] = aprov_vitorias

        estatisticas_gerais = (
            (df_ideal['pontos_por_jogo'] * 0.4) + 
            (df_ideal['rebotes_por_jogo'] * 0.3) + 
            (df_ideal['assistencias_por_jogo'] * 0.3)
        )

        impacto_positivo = np.where(df_ideal['mais_menos'] > 0, df_ideal['mais_menos'], 0)
        impacto_normalizado = impacto_positivo / 10
        bonus_triplo_duplo = 1 + (triple_doubles * 0.02)

        df_ideal['all_nba_index'] = (
            ((estatisticas_gerais * 0.7) + (impacto_normalizado * 0.3)) 
            * bonus_triplo_duplo
        )

        df_elegivel = df_ideal[df_ideal['minutos_por_jogo'] >= 25]
        if len(df_elegivel) == 0:
            df_elegivel = df_ideal[df_ideal['minutos_por_jogo'] >= 15]

        top_all_nba = df_elegivel.sort_values(by='all_nba_index', ascending=False).head(15)

        if 'nome_jogador' not in top_all_nba.columns and 'PLAYER_NAME' in top_all_nba.columns:
            top_all_nba['nome_jogador'] = top_all_nba['PLAYER_NAME']
        if 'sigla_time' not in top_all_nba.columns and 'TEAM_ABBREVIATION' in top_all_nba.columns:
            top_all_nba['sigla_time'] = top_all_nba['TEAM_ABBREVIATION']

        colunas_exibir = [
            'nome_jogador', 'sigla_time', 'jogos_disputados',
            'aproveitamento_vitorias', 'pontos_por_jogo',
            'rebotes_por_jogo', 'assistencias_por_jogo',
            'triple_doubles', 'mais_menos', 'all_nba_index'
        ]
        colunas_disponiveis = [c for c in colunas_exibir if c in top_all_nba.columns]

        st.dataframe(top_all_nba[colunas_disponiveis].reset_index(drop=True), use_container_width=True)