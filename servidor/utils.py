def determina_nivel_soco(forca):
    """
    Determina um 'nível' ou categoria de força com base no valor do acelerômetro.
    Estes valores são apenas exemplos e devem ser calibrados com o hardware real.
    """
    if forca < 10:
        return "Soco de Vento"
    elif forca < 30:
        return "Fraco"
    elif forca < 50:
        return "Médio"
    elif forca < 80:
        return "Forte!"
    else:
        return "DESTRUIDOR!!!"
