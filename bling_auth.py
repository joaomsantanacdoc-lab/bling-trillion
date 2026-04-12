import http.server
import urllib.parse
import webbrowser
import requests
import json
import threading
import base64
import time

# Bling A (funciona)
BLING_A = {
    "client_id": "8ff44703f22759e7a4ce2a45dbfcd94bafd4ab35",
    "client_secret": "979673a5bae4de141f64adcacc5c89bc59db63b3756382981d23577f0247",
    "name": "Bling_A"
}

# Bling B (parado)
BLING_B = {
    "client_id": "d51addbd74b07993c238d2fb67335c7b90c49f56",
    "client_secret": "409144af538be64b1dc318ee2c3ccd7275fea5dc114e9ca6d794fffaee25",
    "name": "Bling_B"
}

TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"
AUTH_URL  = "https://www.bling.com.br/Api/v3/oauth/authorize"
PORT = 8080

auth_code = None

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        print(f"  Recebido: {self.path}")
        if 'code' in params:
            auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("<h1>Autenticado com sucesso! Pode fechar esta aba.</h1>".encode('utf-8'))
        elif 'error' in params:
            erro = params.get('error', [''])[0]
            descricao = params.get('error_description', [''])[0]
            print(f"  Erro Bling: {erro} - {descricao}")
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"<h1>Erro: {erro}</h1><p>{descricao}</p>".encode('utf-8'))
        else:
            print(f"  Parametros recebidos: {params}")
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"<h1>Parametros: {params}</h1>".encode('utf-8'))

    def log_message(self, format, *args):
        pass

def get_tokens(account):
    global auth_code
    auth_code = None

    server = http.server.HTTPServer(('localhost', PORT), OAuthHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.daemon = True
    thread.start()

    auth_url = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={account['client_id']}"
        f"&redirect_uri=http://localhost:{PORT}"
    )
    print(f"\nAbrindo navegador para autenticar {account['name']}...")
    print(f"Se o navegador nao abrir, acesse:\n{auth_url}\n")
    webbrowser.open(auth_url)

    thread.join(timeout=120)
    server.server_close()

    if not auth_code:
        print(f"Erro: timeout aguardando autenticacao de {account['name']}")
        return None

    credentials = base64.b64encode(
        f"{account['client_id']}:{account['client_secret']}".encode()
    ).decode()

    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": f"http://localhost:{PORT}"
        }
    )

    if response.status_code == 200:
        tokens = response.json()
        print(f"  {account['name']} autenticado com sucesso!")
        return tokens
    else:
        print(f"Erro ao obter tokens: {response.status_code} - {response.text}")
        return None

print("=== Autenticacao Bling ===")
print("Serao abertas 2 janelas no navegador.")
print("Faca login em cada uma quando solicitado.\n")

tokens_a = get_tokens(BLING_A)
time.sleep(2)
tokens_b = get_tokens(BLING_B)

if tokens_a and tokens_b:
    data = {
        "bling_a": {"client_id": BLING_A["client_id"], "client_secret": BLING_A["client_secret"], "tokens": tokens_a},
        "bling_b": {"client_id": BLING_B["client_id"], "client_secret": BLING_B["client_secret"], "tokens": tokens_b}
    }
    with open('bling_tokens.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("\nTokens salvos em bling_tokens.json")
    print("Agora rode: python bling_sync.py")
else:
    print("\nErro na autenticacao. Verifique e tente novamente.")
