import streamlit as st

from loader import (
    load_csv,
    get_clients,
    get_client_dataframe
)

from chart_helper import (
    build_salt_chart,
    build_aw_chart
)

st.set_page_config(

    page_title="Sensor Viewer",

    layout="wide"

)

st.title("Sensor Viewer")

uploaded_file = st.file_uploader(

    "Drop CSV file here",

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

clients = get_clients(df)

selected_client = st.selectbox(

    "Client",

    clients

)

client_df = get_client_dataframe(

    df,

    selected_client

)

left, right = st.columns(2)

with left:
    st.plotly_chart(

        build_salt_chart(client_df),

        use_container_width=True

    )

with right:
    st.plotly_chart(

        build_aw_chart(client_df),

        use_container_width=True

    )
