import unicodedata

MIN_OBSERVACOES = 3
QUEDA_MINIMA = 0.10  # 10%

PALAVRAS_PROIBIDAS = [
    "chaveiro", "calculadora", "capa", "pelicula", "suporte",
    "adesivo", "miniatura", "brinquedo", "case para",
]


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def parece_lixo(nome, busca):
    nome_n = normalizar(nome)
    if any(p in nome_n for p in PALAVRAS_PROIBIDAS):
        return True
    return not all(palavra in nome_n for palavra in normalizar(busca).split())


def avaliar(info, est):
    """est = estatisticas() do produto ANTES de salvar o preço novo."""
    if est is None or est["qtd"] < MIN_OBSERVACOES:
        return None

    referencia = est["media"]
    queda = (referencia - info["preco"]) / referencia

    if queda >= QUEDA_MINIMA:
        return {
            "queda": queda,
            "referencia": referencia,
            "menor_historico": info["preco"] < est["minimo"],
        }
    return None