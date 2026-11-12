import os
from pathlib import Path
import pandas as pd
import time
from nba_api.stats.endpoints import leaguedashplayerstats

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

# Caminho relativo seguro usando pathlib (cria a pasta 'data' na raiz do projeto)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

filename = DATA_DIR / "jogadores_nba_2026_27_todas_colunas.csv"

# Salva a base completa com todas as colunas em CSV
df_players.to_csv(filename, index=False)
print(f"\nDados consolidados salvos com sucesso em: {filename}")

time.sleep(1)