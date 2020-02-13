from flask import Flask, request, Response, jsonify
from sesamutils import sesam_logger, VariablesConfig, Dotdictify
from sesamutils.flask import serve
import sys
import msal
import pem
import json
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


class data_access_layer:


    def __init__(self, config):
            self.session = None
            self.auth_token = None
            self.config = config


    def get_token(self):
        cert = config.certificate
        client_credential = {"private_key": cert,"thumbprint": config.cert_thumbprint}
        
        try:
            app = msal.ConfidentialClientApplication(client_id=config.client_id, client_credential=client_credential, authority=config.token_url, validate_authority=True, token_cache=None, verify=True, proxies=None, timeout=None, client_claims=None, app_name=None, app_version=None)    
            result = app.acquire_token_for_client([config.resource])
            if not result["access_token"]:
                logger.error(f"Access token request failed. Error: {resp.content}")
                raise
        except Exception as e:
            logger.error(f"Failed to aquire access_token. Error: {e}")
            raise

        self.auth_token = result["access_token"]
        logger.debug("token: " + self.auth_token)


    def get_entities(self, sites):
        if not self.session:
            self.session = requests.Session()
            self.get_token()

        for site in sites:
            weburl_key = str("webUrl")
            logger.debug(site)
            weburl = self.get_value(site, weburl_key)
            logger.debug(weburl)
            url = weburl + "/_api/web"
            logger.debug("url: " + url)
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
                try:
                    resp = self.session.send(req.prepare())
                except Exception as e:
                    logger.error(f"Failed to send request. Error: {e}")
                    raise

            if not resp.ok:
                error_text = f"Unexpected response status code: {resp.status_code} with response text {resp.text}"
                logger.error(error_text)
                continue

            res = Dotdictify(resp.json())
            id_key = str("_id")
            res['_id'] = self.get_value(site, id_key)
            logger.debug(res)

            yield res


    def get_value(self, entity, target_key):
        for k, v in entity.items():
            if k.split(":")[-1] == target_key:
                res = v
            else:
                pass
        return res
        

DAL = data_access_layer(config)


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


@app.route("/<path:path>", methods=["POST"])
def get(path):

    sites = request.get_json()
    logger.debug(sites)

    entities = DAL.get_entities(sites)
    logger.debug(type(entities))
    logger.debug(entities)

    return Response(stream_json(entities), mimetype='application/json')


if __name__ == '__main__':
    serve(app)