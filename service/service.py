from flask import Flask, request, Response, jsonify
from sesamutils import sesam_logger, VariablesConfig
from sesamutils.flask import serve
import sys
import msal
import pem
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import requests


app = Flask(__name__)

required_env_vars = ["client_id", "certificate", "cert_thumbprint", "token_url", "resource"]
optional_env_vars = ["LOG_LEVEL"]
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)

if hasattr(config, "LOG_LEVEL") and config.LOG_LEVEL == "DEBUG":
    logger = sesam_logger("sharepoint", app=app)
else:
    logger = sesam_logger("sharepoint")


def __init__(self, config):
        self.session = None
        self.auth_token = None
        self.config = config


def get_token()
    cert = config["certificate"]
    client_credential = {"private_key": str(cert[0]),"thumbprint": config["cert_thumbprint"]}
    
    try:
        app = msal.ConfidentialClientApplication(client_id=config["client_id"], client_credential=client_credential, authority=config["token_url"], validate_authority=True, token_cache=None, verify=True, proxies=None, timeout=None, client_claims=None, app_name=None, app_version=None)    
        result = app.acquire_token_for_client([config["resource"]])
        if not result["access_token"]:
            logger.error(f"Access token request failed. Error: {resp.content}")
            raise
    except Exception as e:
        logger.error(f"Failed to aquire access_token. Error: {e}")
        raise

    self.auth_token = result["access_token"]


def get_entities(url)
    if not self.session:
        self.session = requests.Session()
        self.get_token()

    req = requests.Request("GET", url, headers={'accept': 'application/json;odata=nometadata', 'Authorization': 'Bearer ' + self.auth_token})
    try:
        resp = self.session.send(req.prepare())
    except Exception as e:
        logger.error(f"Failed to send request. Error: {e}")
        raise

    if resp.status_code == 401:
        logger.warning("Received status 401. Requesting new access token.")
        self.get_token()
        req = requests.Request("GET", url, headers={'accept': 'application/json;odata=nometadata', 'Authorization': 'Bearer ' + self.auth_token})
        resp = self.session.send(req.prepare())
    return resp.json()


def stream_json(entities):
    first = True
    yield '['
    for i, row in enumerate(entities):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'


@app.route("/<path:path>", methods=["GET"])
def get(path):

    url = path
    logger.debug("url from path: " + str(url))

    entities = stream_json(self.get_entities(url))
    return Response(entities, mimetype='application/json')


if __name__ == '__main__':
    serve(app)