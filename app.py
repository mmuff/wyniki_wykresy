import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Wczytanie danych z pliku Excel
df = pd.read_excel('analiza.xlsx')

st.set_page_config(layout="wide")

# Dodanie zakładek (tabów)
tab1, tab2, tab3 = st.tabs(["Wiarygodność Predykcji", "Statystyki Predykcji", "Wiarygodność dla grup"])

# Tab 1 - Wykresy Wiarygodności
with tab1:
    # Pierwszy wykres: Statystyki wiarygodności
    ad_columns = [col for col in df.columns if col.strip().endswith("- AD")]

    categories = {
        "LOW Reliability": 0,
        "MODERATE Reliability": 0,
        "GOOD Reliability": 0,
        "EXPERIMENTAL value": 0
    }

    for col in ad_columns:
        counts = df[col].value_counts()
        for key in categories.keys():
            categories[key] += counts.get(key, 0)

    plot_data = pd.DataFrame({
        "Kategoria": list(categories.keys()),
        "Liczba": list(categories.values())
    })

    fig1 = px.bar(plot_data, 
                x="Kategoria", 
                y="Liczba", 
                title="Statystyki wiarygodności predykcji w kolumnach '- AD'",
                text="Liczba", 
                color="Kategoria",
                color_discrete_map={
                    "LOW Reliability": "red", 
                    "MODERATE Reliability": "orange", 
                    "GOOD Reliability": "green", 
                    "EXPERIMENTAL value": "blue"
                })

    fig1.update_traces(texttemplate='%{text}', textposition='outside')
    fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    # Drugi wykres: Statystyki wiarygodności dla różnych grup
    groups = ["HBCDDs", "PBDE", "TBBs", "PBBs", "PCBs", "PCDDs", "PCDFs", "OPFRs"]
    reliability_categories = ["LOW Reliability", "MODERATE Reliability", "GOOD Reliability", "EXPERIMENTAL value"]
    colors = {
        "LOW Reliability": "red",
        "MODERATE Reliability": "orange",
        "GOOD Reliability": "green",
        "EXPERIMENTAL value": "blue"
    }

    fig2 = make_subplots(rows=2, cols=4, subplot_titles=groups, shared_yaxes=True)

    for i, grp in enumerate(groups):
        df_group = df[df['group'].str.strip() == grp]

        row = i // 4 + 1
        col = i % 4 + 1

        if df_group.empty:
            fig2.add_annotation(
                text="No data",
                xref="x domain", yref="y domain",
                x=0.5, y=0.5,
                showarrow=False,
                row=row, col=col
            )
            continue

        category_counts = {key: 0 for key in reliability_categories}
        for col_name in ad_columns:
            counts = df_group[col_name].value_counts()
            for key in category_counts.keys():
                category_counts[key] += counts.get(key, 0)

        for category in reliability_categories:
            fig2.add_trace(
                go.Bar(
                    x=[category],
                    y=[category_counts[category]],
                    name=category,
                    marker_color=colors[category],
                    text=[category_counts[category]],
                    textposition="outside",
                    showlegend=True if i == 0 else False
                ),
                row=row, col=col
            )

    # Ukrywanie osi X w drugim wykresie
    fig2.update_xaxes(showticklabels=False)

    fig2.update_layout(
        title="Statystyki wiarygodności predykcji",
        barmode="group",
        height=700,
        width=1200,
        showlegend=False,
        legend_title="Reliability Categories"
    )

    # Wyświetlanie wykresów w aplikacji Streamlit
    st.title("Analiza Wiarygodności Predykcji")

    # Tworzenie dwóch kolumn: jedna dla wykresu 1, druga dla wykresu 2
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)  # Pierwszy wykres

    with col2:
        st.plotly_chart(fig2, use_container_width=True)  # Drugi wykres

# Tab 2 - Statystyki Predykcji
with tab2:
    # Drugi wykres: Statystyki dla różnych endpointów
    endpoint_columns = [col for col in df.columns if col.strip().endswith("- AD")]

    # Lista interesujących kategorii
    reliability_categories = ["LOW Reliability", "MODERATE Reliability", "GOOD Reliability", "EXPERIMENTAL value"]
    colors = {
        "LOW Reliability": "red",
        "MODERATE Reliability": "orange",
        "GOOD Reliability": "green",
        "EXPERIMENTAL value": "blue"
    }

    # Tworzenie subplotów (dynamiczna liczba wierszy i kolumn)
    rows = (len(endpoint_columns) + 2) // 3  # Zaokrąglenie w górę
    cols = min(len(endpoint_columns), 3)  # Maksymalnie 3 kolumny

    fig = make_subplots(
        rows=rows, cols=cols, 
        subplot_titles=endpoint_columns, 
        specs=[[{"type": "pie"}] * cols] * rows
    )

    # Iteracja po każdej kolumnie (endpoint)
    for i, endpoint in enumerate(endpoint_columns):
        row = i // 3 + 1
        col = i % 3 + 1

        # Zliczenie wystąpień interesujących kategorii
        counts = df[endpoint].value_counts().reindex(reliability_categories, fill_value=0)

        # Tworzenie wykresu kołowego dla danego endpointu
        fig.add_trace(
            go.Pie(
                labels=counts.index,
                values=counts.values,
                marker=dict(colors=[colors[cat] for cat in counts.index]),
                textinfo="percent+label",
                showlegend=False
                #showlegend=True if i == 0 else False  # Legenda tylko dla pierwszego wykresu
            ),
            row=row, col=col
        )

    # Aktualizacja wyglądu wykresu
    fig.update_layout(
        title=" ",
        height=300 * rows,  # Automatyczne dopasowanie wysokości
        width=1200,
        showlegend=True,
        font=dict(size=10)  # Zmniejszenie ogólnej czcionki
    )

    # Zmniejszenie czcionki tytułów subplotów + podniesienie ich wyżej
    for i in range(len(endpoint_columns)):
        fig.layout.annotations[i].font.size = 9
        fig.layout.annotations[i].y += 0.018  # Podniesienie tytułu

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Lista grup, dla których chcemy wykresy
    groups = ["HBCDDs", "PBDE", "TBBs", "PBBs", "PCBs", "PCDDs", "PCDFs", "OPFRs"]
    
    # Wybór kolumn, których nazwa kończy się na "- AD" (czyli endpointy)
    endpoint_columns = [col for col in df.columns if col.strip().endswith("- AD")]

    # Definicja interesujących kategorii wiarygodności
    reliability_categories = ["LOW Reliability", "MODERATE Reliability", "GOOD Reliability", "EXPERIMENTAL value"]

    # Definicja kolorów dla poszczególnych kategorii
    color_map = {
        "LOW Reliability": "red",
        "MODERATE Reliability": "orange",
        "GOOD Reliability": "green",
        "EXPERIMENTAL value": "blue"
    }

    # Iteracja po każdym endpointzie
    for endpoint in endpoint_columns:
        # Utworzenie subplots: 2 wiersze x 4 kolumny
        fig = make_subplots(
            rows=2, cols=4,
            specs=[[{'type': 'domain'}]*4]*2,
            subplot_titles=groups
        )
        
        # Iteracja po grupach
        for i, group in enumerate(groups):
            row = i // 4 + 1
            col = i % 4 + 1
            
            # Filtrowanie danych dla danej grupy i endpointu
            df_filtered = df[(df["group"].str.strip() == group) & (df[endpoint].notna())]
            counts = df_filtered[endpoint].value_counts().reindex(reliability_categories, fill_value=0)
            
            # Jeśli są dane, tworzony jest wykres kołowy
            if counts.sum() > 0:
                pie = go.Pie(
                    labels=counts.index,
                    values=counts.values,
                    marker=dict(colors=[color_map[label] for label in counts.index]),
                    textinfo='percent+label'
                )
            else:
                # Gdy brak danych, tworzymy wykres kołowy z jedną szarą wartością "Brak danych"
                pie = go.Pie(
                    labels=["Brak danych"],
                    values=[1],
                    marker=dict(colors=["lightgray"]),
                    textinfo='none'
                )
            fig.add_trace(pie, row=row, col=col)
        
        # Ustawienia układu
        fig.update_layout(
            title_text=f"Endpoint: {endpoint}", 
            #title_x=0.8,  # Ustawienie tytułu na środk
            title_y=1,
            height=500,   # Zmniejszenie wysokości wykresów
            width=1000,   # Zmniejszenie szerokości wykresów
            font=dict(size=8),  # Zmniejszenie czcionki dla całego wykresu
            showlegend=False
        )

        # Zmiana ustawienia tytułów grup: umieszczenie ich nad wykresami, bez nakładania się
        for i in range(len(groups)):
            fig.layout.annotations[i].font.size = 8  # Zmniejszenie czcionki tytułów
            fig.layout.annotations[i].y += 0.18  # Podniesienie tytułów wykresów

        # Wyświetlanie wykresu
        st.plotly_chart(fig, use_container_width=True)


        
        # Ustawienia układu: główny tytuł zawiera nazwę endpointu
        #fig.update_layout(title_text=f"Endpoint: {endpoint}", title_x=0.5)
        #st.plotly_chart(fig, use_container_width=True)
