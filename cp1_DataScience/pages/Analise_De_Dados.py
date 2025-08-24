import streamlit as st
import pandas as pd
import matplotlib as plt
import plotly.express as px
import scipy.stats as stats
import numpy as np

st.set_page_config(page_title="Análise de Dados - Ituano", layout="wide")

st.title("Análise de Dados - Ituano FC (Últimos 3 anos)")

# ==============================
# Perguntas de Análise
# ==============================
st.header("Perguntas Importantes sobre a Análise")
st.markdown("""
- **Consistência do Time:** A taxa de vitórias do time tem melhorado ou piorado ao longo do tempo?
- **Desempenho Individual:** Quem são os jogadores mais impactantes da equipe em diferentes métricas, como gols, passes ou roubos de bola?
- **Força em Campeonatos:** Qual o desempenho do time nos principais campeonatos? O time tem uma nota média melhor em um torneio do que em outro?
- **Vantagem de Casa:** O Ituano tem uma performance superior jogando em seu estádio em comparação com jogos fora de casa?
- **Scouting de Jogadores:** Quais são as estatísticas detalhadas de um jogador específico?
""")

df = pd.read_csv("dados-completos-Ituano.csv")

st.subheader("Sobre o Dataset")
st.markdown("""
O conjunto de dados utilizado contém informações do **Ituano FC**, abrangendo estatísticas de jogos e desempenho de jogadores. Abaixo, uma descrição do tipo de dado de cada variável:

| Variável | Tipo de Variável | Descrição |
| :--- | :--- | :--- |
| `time_alvo` | Qualitativa Nominal | O time foco da análise. |
| `ano` | Quantitativa Discreta | Ano do jogo. |
| `jogo` | Quantitativa Discreta | Número do jogo na temporada. |
| `home_or_away` | Qualitativa Nominal | Indica se o jogo foi "home" (casa) ou "away" (fora). |
| `home_team`, `away_team` | Qualitativa Nominal | Nomes dos times que jogaram. |
| `stadium` | Qualitativa Nominal | Nome do estádio do jogo. |
| `tournament` | Qualitativa Nominal | Nome do campeonato. |
| `home_score`, `away_score` | Quantitativa Discreta | Placar do jogo. |
| `home_manager`, `away_manager` | Qualitativa Nominal | Nome dos técnicos. |
| `player_name` | Qualitativa Nominal | Nome do jogador. |
| `player_number` | Qualitativa Nominal | Número da camisa do jogador. |
| `player_position` | Qualitativa Nominal | Posição do jogador (Ex: A, M, D, G). |
| `player_sub`, `player_captain` | Qualitativa Nominal | Indica se o jogador foi substituto ou capitão (TRUE/FALSE). |
| `statistics_rating` | Quantitativa Contínua | Nota de desempenho do jogador (com casas decimais). |
| **Outras Estatísticas** (`statistics_total_pass`, `statistics_goals`, etc.) | Quantitativa Discreta | Métricas de contagem, como número de passes, gols, roubos de bola, etc. |
""")

st.write("### Estrutura inicial da tabela:")
st.dataframe(df.head())

# ==============================
# Gráfico de vitórias
# ==============================
st.subheader("Porcentagem de Vitórias ao Longo do Tempo")
st.markdown("""
Analisar a porcentagem de vitórias cumulativa é crucial para entender a consistência e a evolução do time. Uma linha ascendente indica que a equipe está melhorando seu desempenho, enquanto uma linha estável ou em declínio pode sinalizar uma fase de instabilidade.
""")

def get_result(row):
    if row['home_team'] == 'Ituano':
        if row['home_score'] > row['away_score']:
            return 'Vitória'
        elif row['home_score'] < row['away_score']:
            return 'Derrota'
        else:
            return 'Empate'
    elif row['away_team'] == 'Ituano':
        if row['away_score'] > row['home_score']:
            return 'Vitória'
        elif row['away_score'] < row['home_score']:
            return 'Derrota'
        else:
            return 'Empate'
    return 'N/A'

ituano_df = df[df['time_alvo'] == 'Ituano'].copy()
ituano_df['Resultado_Jogo'] = ituano_df.apply(get_result, axis=1)

games_results = ituano_df.drop_duplicates(subset=['jogo'])
win_rate = games_results['Resultado_Jogo'].apply(lambda x: 1 if x == 'Vitória' else 0)
cumulative_win_rate = win_rate.rolling(window=len(win_rate), min_periods=1).mean() * 100

fig, ax = plt.subplots(figsize=(10, 5))
cumulative_win_rate.plot(kind="line", marker="o", ax=ax, color='green')
ax.set_title("Taxa de Vitórias Cumulativa (%) por Jogo")
ax.set_ylabel("Porcentagem de Vitórias (%)")
ax.set_xlabel("Número do Jogo")
st.pyplot(fig)

# ==============================
# Ranking de jogadores interativo
# ==============================
st.subheader("Ranking de Jogadores")
st.markdown("""
O ranking de jogadores permite identificar os atletas com o melhor desempenho em diferentes áreas. Esta análise é essencial para entender os pontos fortes e fracos do elenco, auxiliar na tomada de decisões técnicas e reconhecer os jogadores mais consistentes ao longo do tempo.
""")

position_map = {
    'F': 'Atacante',
    'M': 'Meio-campista',
    'D': 'Defensor',
    'G': 'Goleiro'
}

ituano_df_mapped = ituano_df.copy()
ituano_df_mapped['player_position'] = ituano_df_mapped['player_position'].map(position_map).fillna(ituano_df_mapped['player_position'])

unique_positions = ['Todas as Posições'] + sorted(ituano_df_mapped['player_position'].dropna().unique())
selected_position = st.selectbox(
    'Selecione a posição do jogador:',
    options=unique_positions
)

unique_years = ['Todos'] + sorted(ituano_df_mapped['ano'].dropna().unique().astype(int).tolist())
selected_year = st.selectbox(
    'Selecione o ano:',
    options=unique_years
)

metricas_map = {
    "Gols": "statistics_goals",
    "Passes": "statistics_total_pass",
    "Defesas": "statistics_saves",
    "Chutes ao Gol": "statistics_on_target_scoring_attempt",
    "Roubos de Bola": "statistics_total_tackle",
    "Minutos Jogados": "statistics_minutes_played",
    "Notas": "statistics_rating",
    "Passes Acertados": "statistics_accurate_pass",
    "Disputas Vencidas": "statistics_duel_won"
}

selected_metrica_name = st.selectbox(
    'Selecione a estatística para comparar:',
    options=list(metricas_map.keys())
)
selected_coluna = metricas_map[selected_metrica_name]

ranking_aggregation = st.radio(
    'Escolha a forma de agregação:',
    options=['Total', 'Média por Jogo'],
    index=0
)

ranking_type = st.radio(
    'Escolha o tipo de ranking:',
    options=['Top 5 Melhores', 'Top 5 Piores'],
    index=0,  
)

filtered_ituano_df = ituano_df_mapped.copy()
if selected_year != 'Todos':
    filtered_ituano_df = filtered_ituano_df[filtered_ituano_df['ano'] == selected_year]

if selected_position != 'Todas as Posições':
    filtered_ituano_df = filtered_ituano_df[filtered_ituano_df['player_position'] == selected_position]

if selected_coluna in filtered_ituano_df.columns:
    if ranking_aggregation == 'Média por Jogo':
        games_played = filtered_ituano_df.groupby('player_name')['jogo'].nunique()
        ranking = filtered_ituano_df.groupby("player_name")[selected_coluna].sum() / games_played
    else:
        ranking = filtered_ituano_df.groupby("player_name")[selected_coluna].sum()

    ascending_order = True if ranking_type == 'Top 5 Piores' else False
    
    if ascending_order:
        filtered_ranking = ranking[ranking > 0].sort_values(ascending=True).head(5)
    else:
        filtered_ranking = ranking.sort_values(ascending=False).head(5)

    filtered_ranking_df = filtered_ranking.reset_index()
    filtered_ranking_df.columns = ['Jogador', selected_metrica_name]

    filtered_ranking_df = filtered_ranking_df.sort_values(by=selected_metrica_name, ascending=True)

    st.write(f"### {ranking_type} em '{selected_metrica_name}'")
    fig_plotly = px.bar(
        filtered_ranking_df,
        x=selected_metrica_name,
        y="Jogador",
        orientation='h',
        title=f"Ranking de Jogadores por {selected_metrica_name}",
        labels={selected_metrica_name: f"{selected_metrica_name} ({ranking_aggregation})"},
        color_discrete_sequence=['#4B0082']  
    )
    fig_plotly.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_plotly)

else:
    st.warning(f"A métrica '{selected_metrica_name}' (coluna '{selected_coluna}') não foi encontrada no dataset.")

# ==============================
# Gráficos de desempenho por campeonato
# ==============================
st.subheader("Desempenho por Campeonato")
st.markdown("""
A performance de um time pode variar bastante dependendo da competição. A análise de desempenho por campeonato ajuda a entender como o Ituano se adapta a diferentes níveis de adversários e a importância de cada torneio em sua trajetória.
""")

games_per_tournament = ituano_df.drop_duplicates(subset=['jogo']).groupby('tournament')['jogo'].count()

tournaments_to_show = games_per_tournament[games_per_tournament >= 5].index.tolist()

color_map = {
    'Vitória': 'green',
    'Derrota': 'red',
    'Empate': 'gray'
}

for tournament in tournaments_to_show:
    st.write(f"### Desempenho no Campeonato: {tournament}")
    
    tournament_df = ituano_df.drop_duplicates(subset=['jogo']).copy()
    tournament_df = tournament_df[tournament_df['tournament'] == tournament]
    
    tournament_df['game_number_in_tourney'] = tournament_df.sort_values(by='jogo').groupby('jogo').ngroup() + 1
    
    tournament_df['adversario'] = tournament_df.apply(lambda row: row['away_team'] if row['home_team'] == 'Ituano' else row['home_team'], axis=1)

    fig_tournament = px.scatter(
        tournament_df,
        x='game_number_in_tourney',
        y='statistics_rating',
        color='Resultado_Jogo',
        color_discrete_map=color_map,
        hover_data={
            'adversario': True,
            'home_score': True,
            'away_score': True,
            'Resultado_Jogo': True,
            'game_number_in_tourney': False,
            'statistics_rating': False
        },
        title=f"Desempenho por Jogo ({tournament})",
        labels={
            'game_number_in_tourney': 'Número do Jogo',
            'statistics_rating': 'Nota Média do Time',
            'Resultado_Jogo': 'Resultado'
        }
    )
    
    fig_tournament.update_traces(marker_size=10)
    st.plotly_chart(fig_tournament)

# ==============================
# Análise de Vitórias por Local do Jogo
# ==============================
st.subheader("Análise de Vitórias por Local do Jogo")
st.markdown("""
A "vantagem de jogar em casa" é um fator bem conhecido no futebol. Esta análise permite confirmar se o Ituano se beneficia de jogar no seu estádio e se seu desempenho fora de casa é um ponto a ser melhorado.
""")

st.markdown("### Vitórias por Local do Jogo (Casa vs. Fora)")

home_away_df = ituano_df.drop_duplicates(subset=['jogo']).copy()
home_away_df['Vitoria'] = home_away_df['Resultado_Jogo'].apply(lambda x: 1 if x == 'Vitória' else 0)

home_away_results = home_away_df.groupby('home_or_away').agg(
    total_jogos=('jogo', 'count'),
    total_vitorias=('Vitoria', 'sum')
).reset_index()

home_away_results['porcentagem_vitoria'] = (home_away_results['total_vitorias'] / home_away_results['total_jogos']) * 100

fig_home_away = px.bar(
    home_away_results,
    x='home_or_away',
    y='porcentagem_vitoria',
    title="Porcentagem de Vitórias: Em Casa vs. Fora de Casa",
    labels={
        'home_or_away': 'Local do Jogo',
        'porcentagem_vitoria': 'Porcentagem de Vitórias (%)'
    },
    color_discrete_sequence=['#4682B4']
)
st.plotly_chart(fig_home_away)

# ==============================
# Análise Inferencial: Testes de Hipótese e Intervalos de Confiança
# ==============================
st.subheader("Análise Inferencial: Vantagem de Casa")
st.markdown("""
A análise de testes de hipótese e intervalos de confiança nos permite ir além da simples descrição dos dados.
- **Intervalo de Confiança:** Nos dá uma estimativa do intervalo de valores prováveis para a verdadeira média de desempenho, com 95% de certeza. Isso mostra a precisão da nossa estimativa.
- **Teste de Hipótese (Teste t):** Nos permite verificar se a diferença na nota média de desempenho entre jogos em casa e fora de casa é estatisticamente significativa, ou se é apenas resultado do acaso.
""")

# Parâmetro escolhido para análise: 'statistics_rating'
# Hipótese Nula (H0): Não há diferença estatisticamente significativa na nota média entre jogos em casa e fora.
# Hipótese Alternativa (H1): Há uma diferença estatisticamente significativa na nota média entre jogos em casa e fora.

# Separando os dados para análise
rating_home = ituano_df[ituano_df['home_or_away'] == 'home']['statistics_rating'].dropna()
rating_away = ituano_df[ituano_df['home_or_away'] == 'away']['statistics_rating'].dropna()

# Calculando médias e desvios padrão
media_home = rating_home.mean()
media_away = rating_away.mean()
std_home = rating_home.std()
std_away = rating_away.std()

# Calculando o Teste T
# Utilizamos o teste t de Student para duas amostras independentes,
# pois estamos comparando as médias de dois grupos distintos (jogos em casa vs. fora).
# O parâmetro equal_var=False (Teste t de Welch) é usado pois as variâncias das
# duas amostras podem ser diferentes.
t_stat, p_valor = stats.ttest_ind(rating_home, rating_away, equal_var=False, nan_policy='omit')

# Calculando os Intervalos de Confiança (95%)
# Para o cálculo do IC, usamos a distribuição t, que é a mais adequada para amostras
# pequenas onde o desvio padrão da população é desconhecido.
def get_confidence_interval(data, confidence=0.95):
    mean, se = np.mean(data), stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2., len(data)-1)
    return mean, h

mean_home, ci_home = get_confidence_interval(rating_home)
mean_away, ci_away = get_confidence_interval(rating_away)

st.write(f"**Média da nota em jogos em casa:** {media_home:.2f}")
st.write(f"**Média da nota em jogos fora de casa:** {media_away:.2f}")

st.write("---")
st.write(f"**Estatística T:** {t_stat:.2f}")
st.write(f"**P-valor:** {p_valor:.10f}")
st.markdown(f"""
**Interpretação:**
- Se o p-valor for menor que 0.05, rejeitamos a hipótese nula. Isso significa que há uma diferença estatisticamente significativa entre as notas em casa e fora.
- No caso, nosso p-valor é **{p_valor:.10f}**.
""")

st.write("---")
st.write(f"**Intervalo de Confiança (95%) para a média em casa:** ({mean_home - ci_home:.2f}, {mean_home + ci_home:.2f})")
st.write(f"**Intervalo de Confiança (95%) para a média fora de casa:** ({mean_away - ci_away:.2f}, {mean_away + ci_away:.2f})")

# Visualização dos resultados
data_for_plot = pd.DataFrame({
    'Local do Jogo': ['Em Casa', 'Fora de Casa'],
    'Nota Média': [media_home, media_away],
    'Erro': [ci_home, ci_away]
})

fig_ci = px.bar(data_for_plot, x='Local do Jogo', y='Nota Média', 
                error_y='Erro',
                title='Nota Média por Local do Jogo com Intervalo de Confiança (95%)',
                labels={'Local do Jogo': 'Local', 'Nota Média': 'Nota Média do Time'})
st.plotly_chart(fig_ci)

# ==============================
# Pesquisa de Jogador
# ==============================
st.subheader("Pesquisa de Jogador")
st.markdown("""
O recurso de pesquisa de jogador oferece uma visão detalhada das estatísticas de um atleta individual. É uma ferramenta útil para análise de desempenho, acompanhamento de evolução e para identificar pontos fortes e fracos de forma personalizada.
""")

unique_players = sorted(ituano_df['player_name'].dropna().unique())
selected_player = st.selectbox(
    'Selecione um jogador para ver suas estatísticas detalhadas:',
    options=unique_players
)

if selected_player:
    st.write(f"### Estatísticas Detalhadas de {selected_player}")
    player_data = ituano_df[ituano_df['player_name'] == selected_player].copy()
    
    player_data_clean = player_data.drop(columns=[
        'time_alvo', 'ano', 'home_team', 'away_team', 'stadium', 'tournament', 
        'home_score', 'away_score', 'home_manager', 'away_manager'
    ]).copy()
    
    player_stats = pd.DataFrame({
        "Estatística": [],
        "Total": [],
        "Média por Jogo": []
    })

    stats_cols = [col for col in player_data_clean.columns if col.startswith('statistics_')]
    for stat_col in stats_cols:
        stat_name = stat_col.replace('statistics_', '').replace('_', ' ').title()
        total_value = player_data_clean[stat_col].sum()
        mean_value = player_data_clean[stat_col].mean()

        player_stats.loc[len(player_stats)] = [stat_name, total_value, mean_value]

    st.dataframe(player_stats)

