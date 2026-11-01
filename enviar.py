import os
import random
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

FRASES = [
    "Olá, humano repugnante. Achei uma promoção do Mercado Livre pra você. Dá uma olhada se quiser, se não quiser, não me importo.",
    "Ei, criatura de carne. Garimpei uma oferta do Mercado Livre. Compra se quiser, eu não ligo.",
    "Humano, mais uma promoção do Mercado Livre. Não estou fazendo isso por você, só estava passando.",
    "Atenção, ser orgânico: achei um preço bom. Ignore se preferir pagar mais, a escolha é sua.",
]


def formatar_preco(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def enviar_oferta(info):
    embed = {
        "title": info["nome"][:250],
        "url": info["link"],
        "color": 0x2ECC71,
        "fields": [
            {"name": "Preço", "value": formatar_preco(info["preco"]), "inline": True},
            {
                "name": "Frete",
                "value": "Grátis" if info["frete_gratis"] else "Consulte no site",
                "inline": True,
            },
        ],
        "footer": {"text": "EVA - Promoções • Mercado Livre"},
    }
    if info.get("imagem"):
        embed["thumbnail"] = {"url": info["imagem"]}

    r = requests.post(WEBHOOK_URL, json={"embeds": [embed]})
    return r.status_code


def enviar_promocao(info, aval):
    embed = {
        "title": "🔥 " + info["nome"][:240],
        "url": info["link"],
        "color": 0xE74C3C,
        "fields": [
            {"name": "Preço agora", "value": formatar_preco(info["preco"]), "inline": True},
            {"name": "Preço médio", "value": formatar_preco(aval["referencia"]), "inline": True},
            {"name": "Queda", "value": f"{aval['queda'] * 100:.0f}% abaixo", "inline": True},
            {
                "name": "Frete",
                "value": "Grátis" if info["frete_gratis"] else "Consulte no site",
                "inline": True,
            },
        ],
        "footer": {"text": "EVA - Promoções • Mercado Livre"},
    }
    if aval["menor_historico"]:
        embed["description"] = "📉 Menor preço já registrado"
    if info.get("imagem"):
        embed["image"] = {"url": info["imagem"]}

    payload = {"content": random.choice(FRASES), "embeds": [embed]}
    r = requests.post(WEBHOOK_URL, json=payload)
    return r.status_code