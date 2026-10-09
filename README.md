# zynit-agendador

Código do agendador que publica no Instagram (@zynit.oficial) pela API oficial da Meta. **Este repositório não tem conteúdo**: a fila de posts, as legendas e as imagens ficam no repositório privado `zynit-conteudo`.

## Como funciona
1. O cron-job.org chama o GitHub a cada 5 minutos e roda o workflow `.github/workflows/publicar.yml`.
2. O workflow baixa o repositório privado (`CONTEUDO_TOKEN`) e roda `publicar.py`.
3. Para cada item `pendente` com horário vencido, `staging.py` coloca só a mídia daquele post numa branch pública temporária (`staging`), a Meta baixa o arquivo, o post é publicado e a mídia é apagada em seguida.
4. `salvar_fila.py` grava o novo status (publicado, erro, atrasado) no repositório privado, sem apagar edições feitas ao mesmo tempo pelo planejador.
5. Item mais de 6 horas atrasado não é publicado (marca `atrasado`).

Tipos: `feed` (1 imagem JPEG), `carrossel` (2 a 10 JPEG), `story` (JPEG ou MP4), `reel` (MP4).

## Secrets (Settings > Secrets and variables > Actions)
- `IG_TOKEN` e `IG_USER_ID`: API do Instagram (token vale ~60 dias).
- `CONTEUDO_TOKEN`: chave do GitHub só para `zynit-conteudo`, com Contents = Read and write.

## Testar sem publicar
```bash
python publicar.py --dry-run
```
