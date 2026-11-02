import re
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


def parece_lixo(nome, busca, liberar=(), bloquear=()):
    """liberar: palavras da lista padrão que NÃO devem bloquear nesta busca.
    bloquear: palavras extras que devem bloquear só nesta busca."""
    nome_n = normalizar(nome)
    proibidas = [p for p in PALAVRAS_PROIBIDAS if p not in liberar] + list(bloquear)
    for p in proibidas:
        if re.search(rf"\b{re.escape(normalizar(p))}s?\b", nome_n):
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
