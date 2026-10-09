#!/usr/bin/env python3
"""Publica no Instagram os itens vencidos de fila.json (API oficial da Meta).

Variáveis de ambiente: IG_USER_ID, IG_TOKEN, GITHUB_REPOSITORY (owner/repo), GITHUB_TOKEN,
CONTEUDO_DIR (pasta onde está o repositório privado de conteúdo; padrão: ./conteudo).
Uso: python publicar.py [--dry-run]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import staging

API = os.environ.get("IG_API", "https://graph.instagram.com/v25.0")
AQUI = os.path.dirname(os.path.abspath(__file__))
CONTEUDO = os.environ.get("CONTEUDO_DIR") or os.path.join(AQUI, "conteudo")
FILA = os.path.join(CONTEUDO, "fila.json")
TOLERANCIA = timedelta(hours=6)  # item mais atrasado que isso não é publicado
DRY = "--dry-run" in sys.argv


def urls_publicas(midias):
    """Valida os arquivos e os coloca num link público temporário (branch staging)."""
    for m in midias:
        if m.lower().endswith(".png"):
            raise RuntimeError(f"{m}: a API só aceita imagem JPEG; converta para .jpg")
        if not os.path.isfile(os.path.join(CONTEUDO, m)):
            raise RuntimeError(f"{m}: arquivo não encontrado no repositório de conteúdo")
    return staging.enviar([os.path.join(CONTEUDO, m) for m in midias], os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])


def chamar(metodo, caminho, params):
    params = dict(params, access_token=os.environ.get("IG_TOKEN", ""))
    dados = urllib.parse.urlencode(params).encode()
    if metodo == "GET":
        req = urllib.request.Request(f"{API}{caminho}?{dados.decode()}")
    else:
        req = urllib.request.Request(f"{API}{caminho}", data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:500]}") from None


def esperar_container(cid):
    for _ in range(40):
        st = chamar("GET", f"/{cid}", {"fields": "status_code"}).get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {cid} com status {st}")
        time.sleep(15)
    raise RuntimeError(f"container {cid} não ficou pronto a tempo")


def criar(uid, params):
    cid = chamar("POST", f"/{uid}/media", params)["id"]
    esperar_container(cid)
    return cid


def publicar_item(item):
    uid = os.environ["IG_USER_ID"]
    tipo, midias, legenda = item["tipo"], item["midias"], item.get("legenda", "")
    urls = urls_publicas(midias)
    if tipo == "feed":
        cid = criar(uid, {"image_url": urls[0], "caption": legenda})
    elif tipo == "carrossel":
        filhos = [criar(uid, {"image_url": u, "is_carousel_item": "true"}) for u in urls]
        cid = criar(uid, {"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda})
    elif tipo == "story":
        campo = "video_url" if midias[0].lower().endswith(".mp4") else "image_url"
        cid = criar(uid, {"media_type": "STORIES", campo: urls[0]})
    elif tipo == "reel":
        cid = criar(uid, {"media_type": "REELS", "video_url": urls[0], "caption": legenda})
    else:
        raise RuntimeError(f"tipo desconhecido: {tipo}")
    return chamar("POST", f"/{uid}/media_publish", {"creation_id": cid})["id"]


def quem_sou():
    r = chamar("GET", "/me", {"fields": "user_id,username"})
    uid = os.environ.get("IG_USER_ID", "")
    print("username:", r.get("username"))
    print("user_id da API:", r.get("user_id"))
    print("IG_USER_ID bate com user_id:", str(r.get("user_id")) == uid.strip())
    print("tamanho do IG_USER_ID:", len(uid))


def main():
    if "--whoami" in sys.argv:
        quem_sou()
        return
    with open(FILA, encoding="utf-8-sig") as f:
        fila = json.load(f)
    agora = datetime.now(timezone.utc)
    mudou = False
    usou_staging = False
    for item in fila:
        if item.get("status") != "pendente":
            continue
        quando = datetime.fromisoformat(item["data_hora"])
        if quando > agora:
            continue
        if agora - quando > TOLERANCIA:
            item["status"] = "atrasado"
            item["erro"] = "passou da tolerância de 6h; reagende"
            mudou = True
            print(f"[atrasado] {item['id']}")
            continue
        if DRY:
            print(f"[dry-run] publicaria {item['id']} ({item['tipo']}) com {len(item['midias'])} mídia(s)")
            continue
        usou_staging = True
        try:
            item["media_id"] = publicar_item(item)
            item["status"] = "publicado"
            item["publicado_em"] = agora.isoformat()
            print(f"[ok] {item['id']}")
        except Exception as e:  # um erro não trava os outros itens
            item["status"] = "erro"
            item["erro"] = str(e)
            print(f"[erro] {item['id']}: {e}")
        mudou = True
    if usou_staging:
        try:
            staging.limpar(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])
        except Exception as e:  # não derruba o status já obtido
            print("aviso: não consegui limpar a mídia temporária:", e)
    if mudou:
        with open(FILA, "w", encoding="utf-8") as f:
            json.dump(fila, f, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    main()
