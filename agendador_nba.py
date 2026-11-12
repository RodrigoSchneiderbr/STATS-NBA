from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time
import os
import schedule

def executar_ingestao_semanal():
    print("\n[AUTOMATICA] Iniciando a coleta de dados semanais da NBA...")
    
    filename = "nba_jogadores_historico_semanal_2026_27.csv"
    active_players = players.get_active_players()
    all_weekly_games = []
    
    # Define a janela dos últimos 7 dias (ou data de corte desejada)
    data_fim = pd.Timestamp.today()
    one_week_ago = data_fim - pd.Timedelta(days=7)
    
    print(f"Filtrando partidas entre {one_week_ago.strftime('%Y-%m-%d')} e {data_fim.strftime('%Y-%m-%d')}")
    
    for player in active_players:
        player_id = player['id']
        try:
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2026-27', timeout=30)
            df_gamelog = gamelog.get_data_frames()[0]
            
            if not df_gamelog.empty:
                df_gamelog['GAME_DATE'] = pd.to_datetime(df_gamelog['GAME_DATE'])
                recent_games = df_gamelog[
                    (df_gamelog['GAME_DATE'] >= one_week_ago) & 
                    (df_gamelog['GAME_DATE'] <= data_fim)
                ]
                
                if not recent_games.empty:
                    recent_games = recent_games.copy()
                    recent_games['PLAYER_NAME'] = player['full_name']
                    all_weekly_games.append(recent_games)
                    
            time.sleep(1) # Pausa exigida pela API
        except Exception:
            continue

    if len(all_weekly_games) > 0:
        df_new = pd.concat(all_weekly_games, ignore_index=True)
        
        if os.path.exists(filename):
            df_existing = pd.read_csv(filename)
            df_existing['GAME_DATE'] = pd.to_datetime(df_existing['GAME_DATE'])
            
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=['PLAYER_ID', 'GAME_ID'], keep='last')
            df_combined = df_combined.sort_values(by='GAME_DATE', ascending=False)
            
            df_combined.to_csv(filename, index=False)
            print(f"Sucesso! Dados anexados. Total de registros no arquivo: {len(df_combined)}")
        else:
            df_new = df_new.sort_values(by='GAME_DATE', ascending=False)
            df_new.to_csv(filename, index=False)
            print(f"Sucesso! Arquivo criado do zero. Total de registros: {len(df_new)}")
    else:
        print("Nenhum jogo novo encontrado no período.")

# ==========================================
# CONFIGURAÇÃO DO AGENDAMENTO
# ==========================================

# Exemplo: Agendar para rodar toda quarta-feira às 08:00 da manhã
schedule.every().wednesday.at("08:00").do(executar_ingestao_semanal)

# Se quiser testar imediatamente agora para ver funcionando, descomente a linha abaixo:
# executar_ingestao_semanal()

print("Agendador ativado! O script está em execução em segundo plano...")
print("Mantenha o VS Code aberto ou utilize o Agendador de Tarefas do Windows para automação avançada.")

# Loop contínuo que segura o script ativo esperando o dia/horário programado
while True:
    schedule.run_pending()
    time.sleep(1)