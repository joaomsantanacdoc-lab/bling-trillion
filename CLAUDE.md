# Projeto: Bling Sync

## Objetivo
Sincronizar estoque do Bling A (funciona) para o Bling B (parou de sincronizar).

## Contexto
- O sistema da loja (disket.com.br) envia estoque para o Bling A a cada ~15 minutos
- O Bling B parou de receber atualizações (URL antiga da API foi descontinuada)
- Sem acesso ao servidor do ex-programador, criamos solução via GitHub Actions
- URL antiga: `https://bling.com.br/Api/v3` → Nova: `https://api.bling.com.br/Api/v3`

## Fluxo completo
```
Sistema loja (disket.com.br)
        ↓ a cada ~15 min
   Bling A (funciona)

cron-job.org (a cada 15 min)
        ↓ chama GitHub API
   GitHub Actions
        ↓ roda bling_sync.py
   Bling B (sincronizado)
```

## Repositório
- GitHub: https://github.com/joaomsantanacdoc-lab/bling-trillion (privado)
- Pasta local: `C:\Users\João Mateus\bling-sync\`

## Apps Bling criados
| Conta   | Client ID |
|---------|-----------|
| Bling A | `8ff44703f22759e7a4ce2a45dbfcd94bafd4ab35` |
| Bling B | `d51addbd74b07993c238d2fb67335c7b90c49f56` |

- Escopos: Produtos (listagem), Controle avançado de estoque, Depósitos
- Depósito "Geral" Bling B ID: `14888520787`

## Arquivos
- `bling_sync.py` — script principal (roda local e no GitHub Actions)
- `bling_auth.py` — autenticação OAuth inicial (já usado)
- `bling_tokens.json` — tokens locais (no .gitignore)
- `.env` — credenciais locais (no .gitignore)
- `.github/workflows/sync.yml` — workflow GitHub Actions

## GitHub Secrets
- `BLING_A_CLIENT_ID`, `BLING_A_CLIENT_SECRET`, `BLING_A_REFRESH_TOKEN`
- `BLING_B_CLIENT_ID`, `BLING_B_CLIENT_SECRET`, `BLING_B_REFRESH_TOKEN`
- `GH_PAT` — renova refresh tokens automaticamente após cada execução

## Cron externo — cron-job.org
- Job: "BLING" | Intervalo: 15 minutos | Timezone: America/Bahia
- URL: `https://api.github.com/repos/joaomsantanacdoc-lab/bling-trillion/actions/workflows/sync.yml/dispatches`
- Método POST | Body: `{"ref": "main"}`
- Headers: Authorization Bearer GH_PAT, Content-Type application/json, Accept application/vnd.github+json

## Status — CONCLUÍDO em 2026-04-12
- [x] Apps OAuth criados e autenticados em ambas as contas
- [x] Script testado localmente (10 produtos atualizados)
- [x] Código no GitHub, todos os secrets configurados
- [x] GitHub Actions rodando — 1ª execução: SUCESSO (28s, 0 erros)
- [x] Tokens renovados automaticamente a cada execução
- [x] .env e .gitignore configurados
- [x] Cron externo ativo no cron-job.org (dispara a cada 15 min)
