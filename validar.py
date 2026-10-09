#!/usr/bin/env python3
"""Testa um item da fila na API do Instagram SEM publicar.

Coloca a mídia no link temporário, cria o container, espera o processamento e para antes de publicar.
Uso: python validar.py <id do item>   (variáveis: as mesmas do publicar.py)
"""
import json
import os
import sys

import publicar
import staging


def main():
    alvo = sys.argv[1]
    with open(publicar.FILA, encoding="utf-8-sig") as f:
        item = next((i for i in json.load(f) if i["id"] == alvo), None)
    if not item:
        print("item não encontrado:", alvo)
        return 1
    try:
        cid = publicar.publicar_item(item, publicar_agora=False)
        print("OK: a API aceitou a mídia e o container ficou pronto (NADA foi publicado):", cid)
        return 0
    except Exception as e:
        print("FALHOU:", e)
        return 1
    finally:
        try:
            staging.limpar(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])
        except Exception as e:
            print("aviso: não consegui limpar a mídia temporária:", e)


if __name__ == "__main__":
    sys.exit(main())
