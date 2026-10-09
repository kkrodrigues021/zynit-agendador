# zynit-agendador

Publica no Instagram (@zynit.oficial) os posts de `fila.json`, usando a API oficial da Meta e o GitHub Actions. Roda nos servidores do GitHub, com o PC desligado.

## Como funciona
1. As mídias ficam em `midias/` e a fila em `fila.json`.
2. A cada 15 min o workflow `.github/workflows/publicar.yml` roda `publicar.py`.
3. Itens com `status: "pendente"` e `data_hora` já vencida são publicados; o status vira `publicado` (ou `erro`/`atrasado`).
4. Item mais de 6h atrasado não é publicado (marca `atrasado`), para não soltar post velho.

Tipos aceitos: `feed` (1 imagem), `carrossel`, `story` (imagem ou .mp4), `reel` (.mp4).
O repositório precisa ser **público**: a Meta baixa as mídias por URL raw do GitHub.

## Configuração (uma vez, feita por você)
1. Criar o repositório público no GitHub e subir esta pasta.
2. Instagram profissional ligado a uma Página do Facebook.
3. Em developers.facebook.com: criar um app, adicionar o produto de publicação do Instagram, gerar um token de longa duração com permissão de publicar conteúdo e anotar o ID da conta do Instagram.
4. No repositório: Settings > Secrets and variables > Actions > criar `IG_USER_ID` e `IG_TOKEN`. Nunca coloque o token em arquivos nem no chat.
5. Token de longa duração vence em ~60 dias: anote a data para renovar.

Os nomes de permissões e a versão da API (`v21.0` em `publicar.py`) vêm do que conheço da documentação; confira na documentação atual da Meta antes do primeiro uso.

## Testar sem publicar
```bash
python publicar.py --dry-run
```
Só lista o que seria publicado, sem chamar a API.

## Rotina de uso
1. Gerar as mídias e copiar para `midias/<data>/`.
2. Adicionar o item em `fila.json` com `status: "pendente"` e `data_hora` com fuso (`-03:00`).
3. `git add`, `commit`, `push`. O resto é automático.

Melhores horários: ver `../melhores-horarios-instagram.md` (10h em dias úteis, 18h como segundo pico).
