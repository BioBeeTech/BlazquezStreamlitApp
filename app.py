import plotly.graph_objects as go
import streamlit as st

from loader import (
    load_csv,
    get_clients,
    get_client_dataframe
)

from chart_helper import (
    build_combined_chart
)

st.set_page_config(

    page_title="Datalog Viewer",

    layout="wide"

)

st.title("Datalog Viewer")

uploaded_file = st.file_uploader(

    "Arrastra el archivo CSV aquí o haz click para seleccionarlo",

    type=["txt"]

)

if uploaded_file is None:
    st.stop()

df, stats = load_csv(uploaded_file)

if stats["discarded_rows"] > 0:
    st.warning(
        f"Se han descartado {stats['discarded_rows']} registros inválidos "
        f"de un total de {stats['total_rows']}."
    )
else:
    st.success(
        f"CSV cargado correctamente ({stats['valid_rows']} registros)."
    )

if stats["discarded_values"] > 0:
    st.warning(
        f"Se han descartado {stats['discarded_values']} valores fuera de "
        "rango (Sal [0,100], AW [0,1])."
    )

clients = get_clients(df)

# Correspondencia biunívoca CLIENT <-> ALIAS
pairs = df.dropna(subset=["CLIENT", "ALIAS"])[["CLIENT", "ALIAS"]].drop_duplicates("CLIENT")
client_to_alias = {c: str(a) for c, a in zip(pairs["CLIENT"], pairs["ALIAS"])}
alias_to_client = {a: c for c, a in client_to_alias.items()}
aliases = sorted(alias_to_client)

if st.session_state.get("client_sel") not in clients:
    st.session_state["client_sel"] = clients[0]
    st.session_state["alias_sel"] = client_to_alias.get(clients[0])


def _on_client_change():
    st.session_state["alias_sel"] = client_to_alias.get(
        st.session_state["client_sel"]
    )


def _on_alias_change():
    st.session_state["client_sel"] = alias_to_client[
        st.session_state["alias_sel"]
    ]


selected_client = st.selectbox(

    "Cliente",

    clients,

    key="client_sel",

    on_change=_on_client_change

)

st.selectbox(

    "Alias",

    aliases,

    key="alias_sel",

    on_change=_on_alias_change

)

window_days = st.selectbox(

    "Longitud de la ventana (días)",

    [1, 2, 3, 5, 7, 15, 30],

    index=2

)

client_df = get_client_dataframe(

    df,

    selected_client

)

fig = build_combined_chart(client_df, window_days)

st.plotly_chart(

    fig,

    use_container_width=True

)

alias = client_to_alias.get(selected_client, "")

export_fig = go.Figure(fig)
export_fig.update_layout(
    title=dict(text=f"{selected_client}({alias})", x=0.5, xanchor="center"),
    margin=dict(t=100)
)

_, center, _ = st.columns([1, 1, 1])

with center:
    st.download_button(

        "Exportar gráficas (HTML)",

        data=export_fig.to_html(include_plotlyjs=True, full_html=True),

        file_name=f"sensor_{alias or selected_client}"
                  f"_ventana{window_days}d.html",

        mime="text/html",

        use_container_width=True

    )
