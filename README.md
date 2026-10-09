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
Usa a "Instagram API with Instagram Login": não precisa de Página do Facebook, só de conta Instagram **profissional** (comercial ou criador).
1. Acesse developers.facebook.com, entre com o Facebook e crie um app (tipo "Empresa"/Business).
2. No painel do app, adicione o produto **Instagram** e abra "Configuração da API com login do Instagram".
3. Em Funções do app, adicione o @zynit.oficial como testador/desenvolvedor e **aceite o convite** em instagram.com > Configurações > Apps e sites (aba de convites de testador). Sem isso o token não funciona.
4. Na configuração da API, clique em **Gerar token** ao lado da conta, autorize e copie o token (vale 60 dias). Anote também o **ID da conta do Instagram** mostrado ali.
5. No GitHub: repositório > Settings > Secrets and variables > Actions > New repository secret: `IG_TOKEN` (o token) e `IG_USER_ID` (o ID). Nunca cole o token em arquivos nem no chat.
6. Renove o token antes de 60 dias (a doc da Meta tem um endpoint de renovação); anote a data.

Regras da API: imagens **JPEG** (não PNG), mídia em URL pública, até 100 posts por 24h, carrossel até 10 itens.
Confira o passo a passo atual em developers.facebook.com (documentação "Instagram Platform"): os nomes dos menus mudam.

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
