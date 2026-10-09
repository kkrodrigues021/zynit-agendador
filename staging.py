"""Coloca a mídia de um post num lugar público só durante a publicação.

A Meta precisa baixar a imagem ou o vídeo por um link público. O conteúdo fica num repositório
privado; aqui a mídia vai para a branch 'staging' deste repositório público e é apagada logo depois.
A branch é recriada do zero a cada envio (sem histórico).
"""
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
import uuid


def _git(args, cwd):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"git {args[0]} falhou: {r.stderr.strip()[-300:]}")


def _empurrar(arquivos, repo, token):
    """Cria uma branch 'staging' nova só com estes arquivos (nome, caminho) e envia à força."""
    d = tempfile.mkdtemp()
    try:
        _git(["init", "-q", "-b", "staging"], d)
        _git(["config", "user.name", "agendador"], d)
        _git(["config", "user.email", "agendador@users.noreply.github.com"], d)
        for nome, src in arquivos:
            shutil.copy(src, os.path.join(d, nome))
        _git(["add", "-A"], d)
        _git(["commit", "-q", "-m", "staging"], d)
        _git(["push", "-q", "-f", f"https://x-access-token:{token}@github.com/{repo}.git", "HEAD:refs/heads/staging"], d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _esperar(url, tentativas=18):
    for _ in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status in (200, 206):
                    return
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError(f"a mídia não ficou disponível a tempo: {url}")


def enviar(caminhos, repo, token):
    """Envia os arquivos e devolve as URLs públicas, na mesma ordem."""
    pre = uuid.uuid4().hex[:8]
    arquivos = [(f"{pre}-{i:02d}{os.path.splitext(c)[1].lower()}", c) for i, c in enumerate(caminhos, 1)]
    _empurrar(arquivos, repo, token)
    urls = [f"https://raw.githubusercontent.com/{repo}/staging/{nome}" for nome, _ in arquivos]
    for u in urls:
        _esperar(u)
    return urls


def limpar(repo, token):
    """Deixa a branch 'staging' sem nenhuma mídia."""
    d = tempfile.mkdtemp()
    try:
        vazio = os.path.join(d, "LEIAME.txt")
        with open(vazio, "w", encoding="utf-8") as f:
            f.write("vazio\n")
        _empurrar([("LEIAME.txt", vazio)], repo, token)
    finally:
        shutil.rmtree(d, ignore_errors=True)
