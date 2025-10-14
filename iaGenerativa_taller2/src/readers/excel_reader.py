import pandas as pd

# Función para leer Excel
def leer_excel(ruta_excel):
    df = pd.read_excel(ruta_excel, engine='openpyxl')
    texto = ""
    for col in df.columns:
        texto += df[col].to_string(index=False) + "\n"
    return texto