#!/usr/bin/env python3
"""Grava no repositório só as mudanças de status feitas pelo publicador, sem apagar edições
feitas ao mesmo tempo pelo planejador (que também grava fila.json).

Fluxo: compara fila.json local (depois de publicar) com o commit de origem do job, guarda as
diferenças, e reaplica essas diferenças sobre a versão mais nova do repositório, com novas tentativas.
"""
import json
import os
import subprocess
import sys
import time

CAMPOS = ("status", "media_id", "publicado_em", "erro")


def git(*args, check=True):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=check)


def ler(texto):
    return json.loads(texto.lstrip("﻿"))


def main():
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])  # pasta do repositório de conteúdo
    base = {i["id"]: i for i in ler(git("show", "HEAD:fila.json").stdout)}
    with open("fila.json", encoding="utf-8-sig") as f:
        local = ler(f.read())
    mudancas = {}
    for i in local:
        antes = base.get(i["id"], {})
        dif = {c: i.get(c) for c in CAMPOS if i.get(c) != antes.get(c)}
        if dif:
            mudancas[i["id"]] = dif
    if not mudancas:
        print("nada para salvar")
        return 0
    for tentativa in range(1, 6):
        git("fetch", "origin", "main")
        git("reset", "--hard", "origin/main")
        with open("fila.json", encoding="utf-8-sig") as f:
            fila = ler(f.read())
        for item in fila:
            for campo, valor in mudancas.get(item["id"], {}).items():
                if valor is None:
                    item.pop(campo, None)
                else:
                    item[campo] = valor
        with open("fila.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(fila, f, ensure_ascii=False, indent=2)
            f.write("\n")
        if git("diff", "--quiet", "fila.json", check=False).returncode == 0:
            print("fila já está atualizada")
            return 0
        git("add", "fila.json")
        git("commit", "-m", "Atualiza status da fila")
        if git("push", "origin", "HEAD:main", check=False).returncode == 0:
            print("status salvos:", ", ".join(sorted(mudancas)))
            return 0
        print(f"push recusado (tentativa {tentativa}); tentando de novo")
        time.sleep(2 * tentativa)
    print("não foi possível salvar o status da fila", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
