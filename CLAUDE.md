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
        ↓ GitHub Actions scheduler (*/15 * * * *)
   bling_sync.py
        ↓
   Bling B (sincronizado)
```

## Repositório
- GitHub: https://github.com/joaomsantanacdoc-lab/bling-trillion (**público**)
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
- `.github/workflows/sync.yml` — workflow GitHub Actions (cron */15 * * * *)

## GitHub Secrets
- `BLING_A_CLIENT_ID`, `BLING_A_CLIENT_SECRET`, `BLING_A_REFRESH_TOKEN`
- `BLING_B_CLIENT_ID`, `BLING_B_CLIENT_SECRET`, `BLING_B_REFRESH_TOKEN`
- `GH_PAT` — renova refresh tokens automaticamente após cada execução

## Agendamento
- Repo **público** desde 2026-04-12 — scheduler nativo do GitHub Actions funciona gratuitamente
- Cron: `*/15 * * * *` no `.github/workflows/sync.yml`
- cron-job.org foi tentado mas descartado (stripava o header Authorization)

## Status — CONCLUÍDO em 2026-04-12
- [x] Apps OAuth criados e autenticados em ambas as contas
- [x] Script testado localmente (10 produtos atualizados)
- [x] Código no GitHub público, todos os secrets configurados
- [x] GitHub Actions rodando — SUCESSO (0 erros, tokens renovados automaticamente)
- [x] .env e .gitignore configurados
- [x] Repo tornado público para scheduler nativo funcionar
