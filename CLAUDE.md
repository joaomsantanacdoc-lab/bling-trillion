# Projeto: Bling Sync

## Objetivo
Sincronizar estoque do Bling A (funciona) para o Bling B (parou de sincronizar).

## Contexto
- O sistema da loja (disket.com.br) envia estoque para o Bling A a cada ~15 minutos
- O Bling B parou de receber atualizações (URL antiga da API foi descontinuada)
- Este projeto lê o estoque do Bling A e replica no Bling B via GitHub Actions (gratuito, 24/7)

## Contas
- **Bling A**: conta que funciona (leitura de estoque)
- **Bling B**: conta que parou (escrita de estoque)

## Arquivos
- `bling_tokens.json` — tokens de acesso OAuth das duas contas
- `bling_auth.py` — script de autenticação inicial (já usado)
- `bling_sync.py` — script principal de sincronização
- `.github/workflows/sync.yml` — agendamento no GitHub Actions (a cada 15 min)

## Apps criados no Bling
- Bling A — Client ID: 8ff44703f22759e7a4ce2a45dbfcd94bafd4ab35
- Bling B — Client ID: d51addbd74b07993c238d2fb67335c7b90c49f56

## Escopos necessários nos apps
- Produtos: Listagem (para ler produtos e IDs)
- Controle avançado de estoque: Inserção de Estoque
- Depósitos de Estoque

## Status
- [x] Apps criados em ambas as contas
- [x] OAuth autenticado para ambas as contas
- [ ] Adicionar escopo Produtos nos apps
- [ ] Criar script bling_sync.py
- [ ] Configurar GitHub Actions
