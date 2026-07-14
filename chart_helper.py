import plotly.graph_objects as go


def _create_chart(df, title, columns):
    fig = go.Figure()

    for column in columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[column],
                mode="lines+markers",
                name=column.replace("_", " ")
            )
        )

    fig.update_layout(

        title=title,

        xaxis_title="Sample",

        yaxis_title="Value",

        hovermode="x unified",

        template="plotly_white",

        legend=dict(
            orientation="h",
            y=1.05
        )
    )

    return fig


def build_salt_chart(df):
    return _create_chart(

        df,

        "SALT",

        [

            "SALT_LONG",

            "SALT_MEDIUM",

            "SALT_SHORT"

        ]

    )


def build_aw_chart(df):
    return _create_chart(

        df,

        "AW",

        [

            "AW_LONG",

            "AW_MEDIUM",

            "AW_SHORT"

        ]

    )