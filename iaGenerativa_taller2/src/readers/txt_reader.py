def leer_txt(ruta_txt):
    with open(ruta_txt, "r", encoding="utf-8") as file:
        return file.read()