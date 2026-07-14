import pandas as pd

NUMERIC_COLUMNS = [
    "SALT_LONG",
    "SALT_MEDIUM",
    "SALT_SHORT",
    "AW_LONG",
    "AW_MEDIUM",
    "AW_SHORT",
]


def load_csv(file):
    """
    Lee el CSV, valida los datos y devuelve:

        df, stats

    stats contiene información sobre registros válidos
    y descartados.
    """

    df = pd.read_csv(file)

    total_rows = len(df)

    #
    # TIMESTAMP
    #
    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"],
        errors="coerce"
    )

    #
    # Convertir columnas numéricas
    #
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    #
    # Eliminar filas inválidas
    #
    df = df.dropna(
        subset=["TIMESTAMP"] + NUMERIC_COLUMNS
    )

    #
    # Orden cronológico
    #
    df = (
        df
        .sort_values("TIMESTAMP")
        .reset_index(drop=True)
    )

    valid_rows = len(df)

    discarded_rows = total_rows - valid_rows

    stats = {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "discarded_rows": discarded_rows,
    }

    return df, stats


def get_clients(df):
    """
    Devuelve la lista de CLIENT disponibles.
    """

    return sorted(df["CLIENT"].dropna().unique())


def get_client_dataframe(df, client):
    """
    Filtra los registros de un cliente.
    """

    result = (
        df[df["CLIENT"] == client]
        .copy()
        .sort_values("TIMESTAMP")
        .reset_index(drop=True)
    )

    return result
