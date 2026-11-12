import os
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashplayerstats

# Configurações do pandas...
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

print("Buscando estatísticas completas de todos os jogadores para a temporada 2026-27...")

player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2026-27',
    timeout=60
)

df_players = player_stats.get_data_frames()[0]

print(f"\nTotal de jogadores encontrados: {len(df_players)}")

# Garante o caminho absoluto baseado onde extraction_full.py está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

filename = os.path.join(DATA_DIR, "jogadores_nba_2026_27_todas_colunas.csv")

df_players.to_csv(filename, index=False)
print(f"\nDados consolidados salvos com sucesso em: {filename}")

time.sleep(1)