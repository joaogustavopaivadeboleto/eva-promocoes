import os
import requests
from dotenv import load_dotenv

load_dotenv()

API = "https://api.mercadolibre.com"


def gerar_token():
    r = requests.post(
        f"{API}/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("ML_CLIENT_ID"),
            "client_secret": os.getenv("ML_CLIENT_SECRET"),
        },
    )
    r.raise_for_status()
    return r.json()["access_token"]


def buscar_produto(produto_id, token):
    headers = {"Authorization": f"Bearer {token}"}

    r1 = requests.get(f"{API}/products/{produto_id}", headers=headers)
    r2 = requests.get(f"{API}/products/{produto_id}/items", headers=headers)

    if r2.status_code == 404:
        return None  # produto de catálogo sem oferta ativa, é normal

    if r1.status_code != 200 or r2.status_code != 200:
        print("Erro ao consultar", produto_id, r1.status_code, r2.status_code)
        return None

    ofertas = r2.json().get("results", [])
    novas = [o for o in ofertas if o.get("condition") == "new"] or ofertas
    if not novas:
        print("Sem ofertas para", produto_id)
        return None

    melhor = min(novas, key=lambda o: o["price"])

    fotos = r1.json().get("pictures") or []
    imagem = fotos[0].get("url") if fotos else None

    return {
        "id": produto_id,
        "nome": r1.json()["name"],
        "preco": melhor["price"],
        "preco_original": melhor.get("original_price"),
        "frete_gratis": melhor.get("shipping", {}).get("free_shipping", False),
        "ofertas": len(novas),
        "link": f"https://www.mercadolivre.com.br/p/{produto_id}",
        "imagem": imagem,
    }


if __name__ == "__main__":
    token = gerar_token()
    print(buscar_produto("MLB49116229", token))