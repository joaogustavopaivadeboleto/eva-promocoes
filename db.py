import sqlite3
from datetime import datetime, timedelta

CAMINHO = "historico.db"


def conectar():
    con = sqlite3.connect(CAMINHO)
    con.execute(
        """CREATE TABLE IF NOT EXISTS precos (
            produto_id TEXT NOT NULL,
            nome TEXT,
            preco REAL NOT NULL,
            data TEXT NOT NULL
        )"""
    )
    con.execute(
        """CREATE TABLE IF NOT EXISTS alertas (
            produto_id TEXT NOT NULL,
            preco REAL NOT NULL,
            data TEXT NOT NULL
        )"""
    )
    return con


def salvar_preco(info):
    con = conectar()
    con.execute(
        "INSERT INTO precos VALUES (?, ?, ?, ?)",
        (info["id"], info["nome"], info["preco"],
         datetime.now().isoformat(timespec="seconds")),
    )
    con.commit()
    con.close()


def estatisticas(produto_id):
    con = conectar()
    precos = [
        linha[0]
        for linha in con.execute(
            "SELECT preco FROM precos WHERE produto_id = ? ORDER BY data",
            (produto_id,),
        )
    ]
    con.close()

    if not precos:
        return None

    return {
        "qtd": len(precos),
        "minimo": min(precos),
        "ultimo": precos[-1],
        "media": sum(precos) / len(precos),
    }


def registrar_alerta(produto_id, preco):
    con = conectar()
    con.execute(
        "INSERT INTO alertas VALUES (?, ?, ?)",
        (produto_id, preco, datetime.now().isoformat(timespec="seconds")),
    )
    con.commit()
    con.close()


def ja_alertado(produto_id, preco, horas=24):
    con = conectar()
    linha = con.execute(
        "SELECT preco, data FROM alertas WHERE produto_id = ? "
        "ORDER BY data DESC LIMIT 1",
        (produto_id,),
    ).fetchone()
    con.close()

    if not linha:
        return False

    ultimo_preco, data = linha
    recente = datetime.now() - datetime.fromisoformat(data) < timedelta(hours=horas)
    return recente and preco >= ultimo_preco