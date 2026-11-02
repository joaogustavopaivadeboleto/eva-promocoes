import time
import requests
from ml import gerar_token, buscar_produto, API
from db import salvar_preco, estatisticas, registrar_alerta, ja_alertado
from regra import avaliar, parece_lixo
from enviar import enviar_promocao

PAGINAS = 2  # 10 produtos por página

LEGO = {
    "liberar": ["brinquedo", "miniatura"],
    "bloquear": ["compativel", "similar"],
}

# Cada busca: "q" = termos (o nome do produto precisa conter TODAS as palavras).
# "liberar" = palavras da lista proibida que não valem nessa busca.
# "bloquear" = palavras extras proibidas só nessa busca.
BUSCAS = [
    # Peças de computador
    {"q": "placa de vídeo"},
    {"q": "ssd nvme"},
    {"q": "memória ram ddr5"},
    {"q": "processador ryzen"},
    {"q": "gabinete gamer"},
    {"q": "fonte 650w"},
    # Cadeiras
    {"q": "cadeira gamer"},
    {"q": "cadeira escritório"},
    # Periféricos
    {"q": "mouse gamer logitech"},
    {"q": "teclado mecânico redragon"},
    {"q": "headset gamer"},
    {"q": "monitor gamer"},
    {"q": "webcam"},
    # Jogos
    {"q": "ps5 físico"},
    {"q": "ps4 físico"},
    {"q": "switch físico"},
    {"q": "xbox series físico"},
    # LEGO
    {"q": "lego technic", **LEGO},
    {"q": "lego star wars", **LEGO},
    {"q": "lego icons", **LEGO},
    {"q": "lego city", **LEGO},
]


def main():
    token = gerar_token()
    headers = {"Authorization": f"Bearer {token}"}
    analisados = 0
    alertas = 0

    for cfg in BUSCAS:
        busca = cfg["q"]
        liberar = cfg.get("liberar", ())
        bloquear = cfg.get("bloquear", ())
        achados = 0

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
                if not info or parece_lixo(info["nome"], busca, liberar, bloquear):
                    continue

                aval = avaliar(info, estatisticas(info["id"]))  # antes de salvar
                salvar_preco(info)
                analisados += 1
                achados += 1

                if aval and not ja_alertado(info["id"], info["preco"]):
                    status = enviar_promocao(info, aval)
                    if status in (200, 204):
                        registrar_alerta(info["id"], info["preco"])
                        alertas += 1
                        time.sleep(1)
                    else:
                        print(
                            f"Alerta não registrado para {info['id']}: "
                            f"falha no envio ao Discord (status={status})."
                        )

        print(f"  {busca}: {achados} produtos com oferta")

    print(f"Pronto: {analisados} produtos analisados, {alertas} alertas enviados.")


if __name__ == "__main__":
    main()
