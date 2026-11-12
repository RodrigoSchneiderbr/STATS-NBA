from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time

# Configurar o pandas para exibir todas as colunas e linhas sem truncar
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

print("Buscando estatísticas completas de todos os jogadores para a temporada 2026-27...")

# Puxa o endpoint oficial de estatísticas de jogadores
player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2026-27',
    timeout=60
)

# Converte o retorno em um DataFrame do pandas
df_players = player_stats.get_data_frames()[0]

print(f"\nTotal de jogadores encontrados: {len(df_players)}")
print(f"Total de colunas disponíveis: {len(df_players.columns)}")

# Exibe a lista com o nome de todas as colunas capturadas
print("\nColunas disponíveis:")
print(list(df_players.columns))

# Salva a base completa com todas as colunas em CSV
filename = "data/jogadores_nba_2026_27_todas_colunas.csv"
df_players.to_csv(filename, index=False)
print(f"\nDados consolidados salvos com sucesso em: {filename}")

# Pequena pausa recomendada pela documentação do [README](https://github.com/swar/nba_api/blob/master/README.md)
time.sleep(1)