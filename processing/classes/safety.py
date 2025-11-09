from typing import Dict


def calcular_indicador_seguridad_desde_excel(ruta_excel: str, agrupar_por: str = 'COMUNA') -> Dict[str, float]:
    """Lee un archivo Excel de accidentes y devuelve un diccionario
    {grupo: indicador_seguridad} donde `grupo` es el valor de la columna `agrupar_por`.

    Indicador propuesto (simple y explicable):
    - Pondera más los eventos con fallecidos y lesiones graves.
    - indicador = (5*FALLECIDO + 3*GRAVE + 2*M/GRAVE + 1*LEVE) / sqrt(numero_eventos)

    La raíz cuadrada en el denominador reduce la penalización de zonas con muchos eventos,
    ayudando a estabilizar el índice.
    """
    try:
        import pandas as pd
    except Exception as e:
        raise RuntimeError('pandas es requerido para procesar el Excel') from e

    df = pd.read_excel(ruta_excel, dtype={agrupar_por: str})
    # Normalizar nombres para agrupamiento
    df[agrupar_por] = df[agrupar_por].astype(str).str.strip().str.upper()

    # Asegurar columnas numéricas
    for col in ['FALLECIDO', 'GRAVE', 'M/GRAVE', 'LEVE']:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    grupos = df.groupby(agrupar_por)
    indicador: Dict[str, float] = {}

    for nombre, grupo in grupos:
        eventos = len(grupo)
        peso = (5 * grupo['FALLECIDO'].sum() +
                3 * grupo['GRAVE'].sum() +
                2 * grupo['M/GRAVE'].sum() +
                1 * grupo['LEVE'].sum())
        if eventos == 0:
            indicador[nombre] = 0.0
        else:
            indicador[nombre] = float(peso) / (eventos ** 0.5)

    return indicador


def normalizar_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Normaliza los scores a rango [0,1], 1 = más inseguro.
    Si todos los scores son 0, retorna todos 0.
    """
    if not scores:
        return {}
    vals = list(scores.values())
    mn = min(vals)
    mx = max(vals)
    if mx == mn:
        return {k: 0.0 for k in scores}
    return {k: (v - mn) / (mx - mn) for k, v in scores.items()}
