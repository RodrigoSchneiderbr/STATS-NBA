from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time
import os

# Nome do arquivo consolidado onde os dados serão adicionados
filename = "data/nba_jogadores_historico_semanal_2026_27.csv"

print("Buscando lista de jogadores ativos...")
active_players = players.get_active_players()

all_weekly_games = []

data_fim = pd.Timestamp.today()
one_week_ago = data_fim - pd.Timedelta(days=7)

print(f"Filtrando partidas entre {one_week_ago.strftime('%Y-%m-%d')} e {data_fim.strftime('%Y-%m-%d')}")
print("Coletando logs de jogos...\n")

for player in active_players:
    player_id = player['id']
    
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2026-27', timeout=30)
        df_gamelog = gamelog.get_data_frames()[0]
        
        if not df_gamelog.empty:
            df_gamelog['GAME_DATE'] = pd.to_datetime(df_gamelog['GAME_DATE'])
            
            # Filtro considerando a janela semanal E o limite de data máxima (se aplicável)
            recent_games = df_gamelog[
                (df_gamelog['GAME_DATE'] >= one_week_ago) & 
                (df_gamelog['GAME_DATE'] <= data_fim)
            ]
            
            if not recent_games.empty:
                recent_games = recent_games.copy()
                recent_games['PLAYER_NAME'] = player['full_name']
                all_weekly_games.append(recent_games)
                
        # Pausa de segurança exigida pela API
        time.sleep(1)
        
    except Exception as e:
        # Opcional: print(f"Erro ao buscar jogador {player['full_name']}: {e}")
        continue

if len(all_weekly_games) > 0:
    df_new = pd.concat(all_weekly_games, ignore_index=True)
    
    if os.path.exists(filename):
        # Lê o arquivo existente, junta com os novos dados e remove duplicatas
        df_existing = pd.read_csv(filename)
        df_existing['GAME_DATE'] = pd.to_datetime(df_existing['GAME_DATE'])
        
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # Corrigido para nomes de colunas em maiúsculo (padrão da API: PLAYER_ID e GAME_ID)
        df_combined = df_combined.drop_duplicates(subset=['PLAYER_ID', 'GAME_ID'], keep='last')
        df_combined = df_combined.sort_values(by='GAME_DATE', ascending=False)
        
        df_combined.to_csv(filename, index=False)
        print(f"\nDados adicionados (append) com sucesso! Total de registros no arquivo: {len(df_combined)}")
    else:
        # Se o arquivo ainda não existir, cria do zero
        df_new = df_new.sort_values(by='GAME_DATE', ascending=False)
        df_new.to_csv(filename, index=False)
        print(f"\nArquivo criado com sucesso! Total de registros: {len(df_new)}")
else:
    print("\nNenhum jogo novo encontrado no período especificado.")