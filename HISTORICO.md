# Histórico do Projeto Bling Sync

---

## 2026-04-12 — Sessão 1 (João + Claude)

### Problema identificado
- Bling B parou de sincronizar estoque com o sistema da loja
- Ex-programador saiu da empresa, sem acesso ao servidor (disket.com.br)
- Causa: URL antiga da API Bling descontinuada (`https://bling.com.br/Api/v3` → `https://api.bling.com.br/Api/v3`)
- Prazo do Bling para desligar URL antiga: 30/04/2026

### O que foi feito
1. Diagnosticamos o problema pelo painel do Bling (aviso de "Adequação da API necessária")
2. Criamos app OAuth "Sync Estoque" no **Bling A** (privado, escopos: Produtos + Estoque)
3. Criamos app OAuth "Sync Estoque" no **Bling B** (privado, escopos: Produtos + Estoque)
4. Autenticamos ambas as contas via OAuth (fluxo manual com localhost:8080)
5. Criamos `bling_sync.py` — script que lê estoque do Bling A e replica no Bling B
6. Testamos localmente: 10 produtos atualizados, 0 erros
7. Criamos repositório GitHub: `joaomsantanacdoc-lab/bling-trillion` (privado)
8. Configuramos 7 GitHub Secrets (credenciais + GH_PAT)
9. Configuramos GitHub Actions (`sync.yml`) para rodar a cada 15 min
10. Primeira execução no GitHub Actions: SUCESSO (28s, 0 erros, tokens renovados)
11. Configuramos cron-job.org como disparador externo (mais confiável que o scheduler do GitHub)
12. Criado `.env` local com credenciais, adicionado ao `.gitignore`

### Resultado
Bling B agora sincroniza automaticamente com Bling A a cada 15 minutos, 24/7, sem depender do servidor do ex-programador.

### Próximas sessões — verificar
- Confirmar que o cron-job.org está disparando corretamente
- Monitorar execuções no GitHub Actions
- Se aparecer erro de token, re-autenticar via `bling_auth.py`
