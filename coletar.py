import time
import requests
from ml import gerar_token, buscar_produto, API
from db import salvar_preco, estatisticas, registrar_alerta, ja_alertado
from regra import avaliar, parece_lixo
from enviar import enviar_promocao

BUSCAS = ["mouse gamer logitech", "teclado mecânico redragon", "headset gamer"]
PAGINAS = 2  # 10 produtos por página


def main():
    token = gerar_token()
    headers = {"Authorization": f"Bearer {token}"}
    analisados = 0
    alertas = 0

    for busca in BUSCAS:
        for pagina in range(PAGINAS):
            r = requests.get(
                f"{API}/products/search",
                headers=headers,
                params={
                    "status": "active",
                    "site_id": "MLB",
                    "q": busca,
                    "offset": pagina * 10,
                },
            )
            if r.status_code != 200:
                print("Erro na busca:", busca, r.status_code)
                break

            for p in r.json().get("results", []):
                info = buscar_produto(p["id"], token)
                if not info or parece_lixo(info["nome"], busca):
                    continue

                aval = avaliar(info, estatisticas(info["id"]))  # antes de salvar
                salvar_preco(info)
                analisados += 1

                if aval and not ja_alertado(info["id"], info["preco"]):
                    enviar_promocao(info, aval)
                    registrar_alerta(info["id"], info["preco"])
                    alertas += 1
                    time.sleep(1)

    print(f"Pronto: {analisados} produtos analisados, {alertas} alertas enviados.")


if __name__ == "__main__":
    main()