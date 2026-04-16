import requests
import base64
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # carrega .env quando rodando localmente

BASE_URL = 'https://api.bling.com.br/Api/v3'
TOKEN_URL = 'https://www.bling.com.br/Api/v3/oauth/token'
TOKENS_FILE = 'bling_tokens.json'
DEPOSITO_B_ID = 14888520787  # Deposito "Geral" do Bling B

IN_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS') == 'true'


def load_tokens():
    if IN_GITHUB_ACTIONS:
        return {
            'bling_a': {
                'client_id':     os.environ['BLING_A_CLIENT_ID'],
                'client_secret': os.environ['BLING_A_CLIENT_SECRET'],
                'access_token':  '',
                'refresh_token': os.environ['BLING_A_REFRESH_TOKEN'],
            },
            'bling_b': {
                'client_id':     os.environ['BLING_B_CLIENT_ID'],
                'client_secret': os.environ['BLING_B_CLIENT_SECRET'],
                'access_token':  '',
                'refresh_token': os.environ['BLING_B_REFRESH_TOKEN'],
            }
        }
    with open(TOKENS_FILE) as f:
        data = json.load(f)
    # Suporta tanto o formato flat quanto o formato com chave "tokens" gerado pelo bling_auth.py
    for key in ('bling_a', 'bling_b'):
        if 'tokens' in data[key]:
            nested = data[key].pop('tokens')
            data[key].update(nested)
    return data


def save_tokens(tokens):
    if IN_GITHUB_ACTIONS:
        update_github_secret('BLING_A_REFRESH_TOKEN', tokens['bling_a']['refresh_token'])
        update_github_secret('BLING_B_REFRESH_TOKEN', tokens['bling_b']['refresh_token'])
    else:
        with open(TOKENS_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)


def update_github_secret(name, value):
    import nacl.public
    import nacl.encoding

    token  = os.environ['GH_PAT']
    repo   = os.environ['GITHUB_REPOSITORY']
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    key_resp = requests.get(
        f'https://api.github.com/repos/{repo}/actions/secrets/public-key',
        headers=headers
    ).json()

    pk = nacl.public.PublicKey(key_resp['key'], nacl.encoding.Base64Encoder)
    encrypted = base64.b64encode(nacl.public.SealedBox(pk).encrypt(value.encode())).decode()

    requests.put(
        f'https://api.github.com/repos/{repo}/actions/secrets/{name}',
        headers=headers,
        json={'encrypted_value': encrypted, 'key_id': key_resp['key_id']}
    )
    print(f'  Secret {name} atualizado.')


def refresh_access_token(account):
    credentials = base64.b64encode(
        f"{account['client_id']}:{account['client_secret']}".encode()
    ).decode()

    resp = requests.post(
        TOKEN_URL,
        headers={
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data={
            'grant_type': 'refresh_token',
            'refresh_token': account['refresh_token']
        }
    )

    if resp.status_code == 200:
        data = resp.json()
        account['access_token']  = data['access_token']
        account['refresh_token'] = data['refresh_token']
        print('  Token renovado.')
        return True
    else:
        print(f'  Erro ao renovar token: {resp.status_code} - {resp.text}')
        return False


def api_get(account, url, params=None):
    resp = requests.get(url, headers={'Authorization': f'Bearer {account["access_token"]}'}, params=params)
    if resp.status_code == 401:
        if refresh_access_token(account):
            resp = requests.get(url, headers={'Authorization': f'Bearer {account["access_token"]}'}, params=params)
    return resp


def get_all_products(account):
    products = {}
    page = 1
    while True:
        resp = api_get(account, f'{BASE_URL}/produtos', {'limite': 100, 'pagina': page, 'situacao': 'A'})
        if resp.status_code != 200:
            print(f'  Erro ao buscar produtos (pag {page}): {resp.status_code}')
            break
        data = resp.json().get('data', [])
        if not data:
            break
        for p in data:
            products[p['codigo']] = {
                'id':     p['id'],
                'nome':   p['nome'],
                'estoque': p.get('estoque', {}).get('saldoVirtualTotal', 0)
            }
        page += 1
        time.sleep(0.3)
    return products


def update_stock(account, product_id, quantity):
    resp = requests.post(
        f'{BASE_URL}/estoques',
        headers={
            'Authorization': f'Bearer {account["access_token"]}',
            'Content-Type': 'application/json'
        },
        json={
            'produto':    {'id': product_id},
            'deposito':   {'id': DEPOSITO_B_ID},
            'operacao':   'B',
            'quantidade': quantity,
            'preco':      0,
            'observacoes': 'Sync automatico Bling A -> Bling B'
        }
    )
    if resp.status_code == 401:
        if refresh_access_token(account):
            return update_stock(account, product_id, quantity)
    return resp.status_code, resp.json() if resp.text else {}


def sync():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando sincronizacao...")

    tokens = load_tokens()
    a = tokens['bling_a']
    b = tokens['bling_b']

    # Renovar tokens e salvar IMEDIATAMENTE antes de qualquer outra coisa
    print('Renovando tokens...')
    ok_a = refresh_access_token(a)
    ok_b = refresh_access_token(b)

    if not ok_a or not ok_b:
        print('Falha ao renovar tokens. Abortando para nao perder tokens validos.')
        return

    save_tokens(tokens)
    print('  Tokens salvos com sucesso.')

    print('Lendo produtos do Bling A...')
    produtos_a = get_all_products(a)
    print(f'  {len(produtos_a)} produtos encontrados')

    print('Lendo produtos do Bling B...')
    produtos_b = get_all_products(b)
    print(f'  {len(produtos_b)} produtos encontrados')

    atualizados = ignorados = erros = 0

    for codigo, prod_a in produtos_a.items():
        if codigo not in produtos_b:
            ignorados += 1
            continue

        prod_b   = produtos_b[codigo]
        estoque_a = prod_a['estoque']
        estoque_b = prod_b['estoque']

        if estoque_a == estoque_b:
            ignorados += 1
            continue

        status, resp = update_stock(b, prod_b['id'], estoque_a)
        if status in (200, 201):
            print(f'  OK {codigo} | {prod_a["nome"][:40]} | {estoque_b} -> {estoque_a}')
            atualizados += 1
        else:
            print(f'  ERRO {codigo}: {resp}')
            erros += 1

        time.sleep(0.3)

    print(f'\nFinalizado: {atualizados} atualizados | {ignorados} sem alteracao | {erros} erros')


if __name__ == '__main__':
    sync()
