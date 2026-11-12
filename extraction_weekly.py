import os
from pathlib import Path
import pandas as pd
import time
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

# Caminho relativo seguro usando pathlib
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

filename = DATA_DIR / "nba_jogadores_historico_semanal_2026_27.csv"

print("Buscando lista de jogadores ativos...")
active_players = players.get_active_players()

all_weekly_games = []

data_fim = pd.Timestamp.today()
one_week_ago = data_fim - pd.Timedelta(days=7)

print(f"Filtrando partidas entre {one_week_ago.strftime('%Y-%m-%d')} e {data_fim.strftime('%Y-%m-%d')}")
print(f"Total de jogadores na base para verificar: {len(active_players)}")
print("Coletando logs de jogos (isso pode levar alguns minutos)...\n")

for i, player in enumerate(active_players):
    player_id = player['id']
    player_name = player['full_name']
    
    try:
        # Timeout reduzido para evitar travamentos longos
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2026-27', timeout=15)
        df_gamelog = gamelog.get_data_frames()[0]
        
        if not df_gamelog.empty:
            df_gamelog['GAME_DATE'] = pd.to_datetime(df_gamelog['GAME_DATE'])
            
            recent_games = df_gamelog[
                (df_gamelog['GAME_DATE'] >= one_week_ago) & 
                (df_gamelog['GAME_DATE'] <= data_fim)
            ]
            
            if not recent_games.empty:
                recent_games = recent_games.copy()
                recent_games['PLAYER_NAME'] = player_name
                all_weekly_games.append(recent_games)
                print(f"[{i+1}/{len(active_players)}] {player_name}: {len(recent_games)} jogo(s) recente(s) encontrado(s).")
                
        # Pausa dinâmica leve para respeitar a API
        time.sleep(0.6)
        
    except Exception:
        # Silencia erros de timeout pontuais de jogadores que não jogaram na temporada
        time.sleep(1)
        continue

if len(all_weekly_games) > 0:
    df_new = pd.concat(all_weekly_games, ignore_index=True)
    
    if filename.exists():
        df_existing = pd.read_csv(filename)
        df_existing['GAME_DATE'] = pd.to_datetime(df_existing['GAME_DATE'])
        
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=['PLAYER_ID', 'GAME_ID'], keep='last')
        df_combined = df_combined.sort_values(by='GAME_DATE', ascending=False)
        
        df_combined.to_csv(filename, index=False)
        print(f"\n✅ Dados semanais adicionados com sucesso! Total de registros no arquivo: {len(df_combined)}")
    else:
        df_new = df_new.sort_values(by='GAME_DATE', ascending=False)
        df_new.to_csv(filename, index=False)
        print(f"\n✅ Arquivo semanal criado com sucesso! Total de registros: {len(df_new)}")
else:
    print("\n⚠️ Nenhum jogo novo encontrado no período especificado.")