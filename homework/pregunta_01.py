"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""

import pandas as pd
import os
import unicodedata
import re


def pregunta_01():
    """
    Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".
    El archivo tiene problemas como registros duplicados y datos faltantes.
    Tenga en cuenta todas las verificaciones discutidas en clase para
    realizar la limpieza de los datos.

    El archivo limpio debe escribirse en "files/output/solicitudes_de_credito.csv"
    """

    # 1. Leer el archivo
    df = pd.read_csv("files/input/solicitudes_de_credito.csv", sep=";", index_col=0)

    # 2. Eliminar filas con valores faltantes
    df.dropna(inplace=True)

    # 3. Normalizar nombres de columnas
    df.columns = [
        "sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "estrato",
        "comuna_ciudadano", "fecha_de_beneficio", "monto_del_credito", "línea_credito"
    ]

    # 4. Función de limpieza de texto
    def clean_text(s):
        s = s.astype(str).str.lower()
        # Reemplazar separadores por espacio
        s = s.str.replace("_", " ").str.replace("-", " ")
        # Eliminar caracteres de reemplazo de encoding corrupto (ej. ¿)
        s = s.str.replace(r"[^\w\s]", "", regex=True)
        # Eliminar acentos
        s = s.apply(
            lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8")
        )
        # Colapsar espacios múltiples
        s = s.str.replace(r"\s+", " ", regex=True)
        return s

    # 5. Aplicar limpieza a columnas de texto
    for col in ["sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito"]:
        df[col] = clean_text(df[col])

    # 6. Limpiar monto_del_credito
    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .astype(str)
        .str.replace(r"[$,]", "", regex=True)
        .str.strip()
        .astype(float)
        .astype(int)
    )

    # 7. Estandarizar fecha_de_beneficio con parseo MIXTO
    # El CSV mezcla DD/MM/YYYY y YYYY/MM/D
    fechas_raw = df["fecha_de_beneficio"].astype(str)
    fechas = pd.to_datetime(fechas_raw, dayfirst=True, errors="coerce")
    mask_nat = fechas.isna()
    fechas[mask_nat] = pd.to_datetime(fechas_raw[mask_nat], dayfirst=False, errors="coerce")
    df["fecha_de_beneficio"] = fechas.dt.strftime("%Y-%m-%d")

    # 8. Normalizar tipos numéricos
    df["estrato"] = df["estrato"].astype(int)
    df["comuna_ciudadano"] = df["comuna_ciudadano"].astype(float).astype(int)

    # 9. Eliminar duplicados DESPUÉS de la normalización completa
    df.drop_duplicates(inplace=True)

    # 10. Guardar el archivo limpio
    os.makedirs("files/output", exist_ok=True)
    df.to_csv("files/output/solicitudes_de_credito.csv", sep=";", index=False)

    return df
