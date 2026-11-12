# 🏀 Dashboard Analítico da NBA (Temporada 2026-27)

Dashboard analítico desenvolvido em **Streamlit** e **Python** para monitoramento avançado de estatísticas da temporada 2026-27 da NBA. O projeto combina métricas personalizadas e comportamentais para além do basquete tradicional, avaliando ineficiência ofensiva, impacto defensivo real e consistência de elite.

---

## 📊 Métricas Personalizadas Desenvolvidas

1. **🔥 Peladeiro Master:** Métrica focada em ineficiência de arremessos de 3 pontos (volume ponderado pelo erro ao quadrado), índice de desperdícios/faltas (anti-defesa) e o prejuízo direto causado no saldo de pontos da equipe (`PLUS_MINUS` negativo).
2. **🛡️ Defensor Elite:** Avalia cães de guarda em quadra cruzando atividade pura (roubos e tocos ponderados), atenuando o rebote defensivo passivo, normalizando o impacto positivo no placar e aplicando um fator de disciplina por faltas pessoais, ajustado pelo aproveitamento real de vitórias do atleta em quadra (`W / (W + L)`).
3. **⭐ All-NBA Teams:** Mede o equilíbrio de elite considerando pontuação, rebotes e assistências por jogo, saldo positivo normalizado e um bônus multiplicador de versatilidade baseado na acumulação de triplo-duplos.

---

## 🛠️ Tecnologias e Stack Utilizadas

* **Python 3.11+**
* **Streamlit** (Interface gráfica web interativa)
* **Pandas & NumPy** (Manipulação, limpeza e vetorização matemática de dados)
* **Git & GitHub** (Versionamento de código)

---

## 📂 Estrutura do Projeto

```text
nba/
│
├── data/
│   └── jogadores_nba_2026_27_todas_colunas.csv  # Fonte única de verdade (estatísticas consolidadas)
│
├── .gitignore          # Arquivos e pastas ignoradas pelo Git
├── requirements.txt    # Dependências do projeto
├── extracao_full.py    # Script de extração completa/histórica da temporada
├── extracao_weekly.py  # Script de extração e logs semanais
├── app.py              # Aplicação principal em Streamlit
└── README.md           # Documentação oficial do projeto

```
## Rodando local

``` text
pip install -r requirements.txt
```
```text
streamlit run app.py
```
