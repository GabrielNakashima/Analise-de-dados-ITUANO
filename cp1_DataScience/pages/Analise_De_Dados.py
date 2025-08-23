import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Análise de Dados - Ituano", layout="wide")

st.title("📊 Análise de Dados - Ituano FC")

df = pd.read_csv("dados-completos-Ituano.csv")

st.subheader("📖 Sobre o Dataset")
st.markdown("""
O conjunto de dados utilizado contém informações do **Ituano FC**, abrangendo
estatísticas de jogos e desempenho de jogadores.  

Exemplos de variáveis:
- `home_score` e `away_score`: placar do jogo
- `player_name`: nome do jogador
- `statistics_goals`: gols marcados, etc.
""")

st.write("### Estrutura inicial da tabela:")
st.dataframe(df.head())

st.subheader("📈 Porcentagem de Vitórias ao Longo do Tempo")

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

st.subheader("🏆 Ranking de Jogadores")

position_map = {
    'A': 'Atacante',
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

metricas_map = {
    "Gols": "statistics_goals",
    "Passes": "statistics_total_pass",
    "Defesas": "statistics_saves",
    "Chutes no Alvo": "statistics_on_target_scoring_attempt",
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

    st.write(f"### 🔹 {ranking_type} em '{selected_metrica_name}'")
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

st.subheader("📊 Desempenho por Campeonato")

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

st.subheader("📊 Análise de Vitórias por Local do Jogo")

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

st.subheader("🔍 Pesquisa de Jogador")

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
