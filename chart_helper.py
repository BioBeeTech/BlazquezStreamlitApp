import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _missing_days(timestamps):
    days = set(timestamps.dt.normalize().unique())
    all_days = pd.date_range(min(days), max(days), freq="D")
    return [d.strftime("%Y-%m-%d") for d in all_days if d not in days]


GRID_COLOR = "#404040"
BOX_COLOR = "gray"
DEFAULT_WINDOW_DAYS = 3
TRACE_COLORS = ["#636EFA", "#EF553B", "#00CC96"]  # LONG, MEDIUM, SHORT


def _create_chart(df, title, columns, window_days=DEFAULT_WINDOW_DAYS):
    return _create_figure(df, [(title, columns)], window_days)


def _create_figure(df, groups, window_days=DEFAULT_WINDOW_DAYS):
    """
    Una gráfica por grupo (title, columns), apiladas verticalmente
    y con el eje X enlazado (zoom/pan sincronizados).
    """
    rows = len(groups)

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12 if rows > 1 else 0,
    )

    ts = df["TIMESTAMP"].dt.tz_localize(None)

    # Ancho explícito (ms): el automático depende del par de registros más cercano
    gaps = ts.drop_duplicates().sort_values().diff().dropna()
    bar_width = gaps.median().total_seconds() * 1000 * 0.8 if len(gaps) else 86400000 * 0.8

    for row, (_, columns) in enumerate(groups, start=1):
        for index, column in enumerate(columns):
            fig.add_trace(
                go.Bar(
                    x=ts,
                    y=df[column],
                    width=bar_width / len(columns),
                    offset=(index - len(columns) / 2) * bar_width / len(columns),
                    name=column.replace("_", " "),
                    marker=dict(color=TRACE_COLORS[index]),
                    legend="legend" if row == 1 else f"legend{row}"
                ),
                row=row,
                col=1
            )

            # Media deslizante diaria: para cada día d, promedio de todas las
            # muestras de los días d .. d+window_days-1 (truncado al final)
            origin = ts.min().normalize()
            day_idx = ((ts - origin).dt.days).to_numpy()
            values = df[column].to_numpy(dtype=float)
            ok = ~np.isnan(values)

            line_x, line_y = [], []
            for d in range(int(day_idx.max()) + 1):
                mask = ok & (day_idx >= d) & (day_idx < d + window_days)
                if mask.any():
                    line_x.append(origin + pd.Timedelta(days=d, hours=12))
                    line_y.append(values[mask].mean())

            if line_x:
                fig.add_trace(
                    go.Scatter(
                        x=line_x,
                        y=line_y,
                        mode="lines",
                        name=column.replace("_", " ") + " media",
                        line=dict(
                            color=TRACE_COLORS[index],
                            width=2,
                            shape="spline",
                            smoothing=1.0,
                        ),
                        legend="legend" if row == 1 else f"legend{row}"
                    ),
                    row=row,
                    col=1
                )

    fig.update_xaxes(
        type="date",
        #rangebreaks=[dict(values=_missing_days(ts))],
        tickformat="%d/%m/%y",
        tickmode="linear",
        tick0=ts.min().normalize(),
        dtick=86400000,
        tickangle=-90,
        showticklabels=True,
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        gridwidth=0.5,
        showline=True,
        linecolor=BOX_COLOR,
        mirror=True,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        gridwidth=0.5,
        showline=True,
        linecolor=BOX_COLOR,
        mirror=True,
    )

    fig.update_layout(

        height=350 * rows + 100 * (rows > 1),

        margin=dict(l=10, r=150, t=60, b=10),

        barmode="group",

        hovermode="x unified",

        template="plotly_white"
    )

    # Una leyenda por gráfica, fuera del box (a la derecha) y alineada
    # con su parte superior
    for row in range(1, rows + 1):
        yaxis = fig.layout.yaxis if row == 1 else fig.layout[f"yaxis{row}"]
        top = yaxis.domain[1]

        fig.update_layout(**{
            "legend" if row == 1 else f"legend{row}": dict(
                orientation="v",
                x=1.01,
                xanchor="left",
                y=top,
                yanchor="top"
            )
        })

    for row, (title, _) in enumerate(groups, start=1):
        fig.update_yaxes(title_text=title, row=row, col=1)

    return fig


SALT_COLUMNS = ["SALT_LONG", "SALT_MEDIUM", "SALT_SHORT"]
AW_COLUMNS = ["AW_LONG", "AW_MEDIUM", "AW_SHORT"]


def build_combined_chart(df, window_days=DEFAULT_WINDOW_DAYS):
    return _create_figure(

        df,

        [

            ("SALT", SALT_COLUMNS),

            ("AW", AW_COLUMNS)

        ],

        window_days

    )


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