# -*- coding: utf-8 -*-

import datetime
import os
import random
from camel_parser.src.conll_output import print_to_conll, text_tuples_to_string
from camel_parser.src.data_preparation import get_file_type_params, parse_text
import flask
import requests
from flask import request
from pandas import read_csv
from camel_tools.utils.charmap import CharMapper

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from flask_cors import CORS, cross_origin
import sys
sys.path.insert(0,'camel_parser/src')

from dotenv import load_dotenv
load_dotenv('.env')


project_dir = os.path.expanduser('~/palmyra_server/palmyra_server')
# for local dev
# project_dir = os.path.expanduser('.')

# camel_tools import used to clean text
arclean = CharMapper.builtin_mapper("arclean")

#
### Get clitic features
#
clitic_feats_df = read_csv(f'{project_dir}/camel_parser/data/clitic_feats.csv')
clitic_feats_df = clitic_feats_df.astype(str).astype(object) # so ints read are treated as string objects



# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = f"{os.path.expanduser(project_dir)}/client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = os.getenv('FLASK_SECRET')

# app.config['CORS_HEADERS'] = 'Content-Type'

# cors = CORS(app, resources={r"/test": {"origins": 'https://voluble-fudge-4fc88e.netlify.app/'}})
cors = CORS(app, supports_credentials=True)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/parse_data', methods=['POST'])
def parse_data():
  lines = request.get_json()['sentences']
  parser_type = request.get_json()['parserType']
  file_type = 'text'
  
  if parser_type == "ar_catib":
    parser_model_name = "CAMeLBERT-CATiB-biaffine.model"
  elif parser_type == "ar_ud":
    parser_model_name = "CAMeLBERT-UD-biaffine.model"
  else:
    # just in case user messes with html
    return
  
  file_type_params = get_file_type_params(lines, file_type, '', f'{project_dir}/camel_parser/models/{parser_model_name}',
      arclean, 'bert', clitic_feats_df, 'catib6', 'calima-msa-s31')
  parsed_text_tuples = parse_text(file_type, file_type_params)

  string_lines = text_tuples_to_string(parsed_text_tuples, sentences=lines)
  parsed_data = '\n'.join(string_lines)

  new_id = str(int(random.random()*100000)) + datetime.datetime.now().strftime('%s')
  
  with open(f'{project_dir}/data/temp_parsed/{new_id}', 'w') as f:
    f.write(parsed_data)

  return new_id


@app.route('/get_parsed_data', methods=['GET'])
def get_parsed_data():
  data_id = request.args.get("data_id")
  conll_file_path = f'{project_dir}/data/temp_parsed/{data_id}'
  
  data = []
  with open(conll_file_path, 'r') as f:
    data = f.readlines()
  os.remove(conll_file_path)
  
  return ''.join(data)

@app.route('/get_gapi_credentials', methods=['GET'])
def get_gapi_credentials():
  return {
    'apiKey': os.getenv('GCP_API_KEY'),
    'discovertDocs': [os.getenv('GCP_DISCOVERY_DOC')]
  }

@app.route('/get_gis_credentials', methods=['GET'])
def get_gis_credentials():
  return {
    'client_id': os.getenv('GCP_CLIENT_ID'),
    'scope': SCOPES
  }

if __name__ == '__main__':
  project_dir = os.path.expanduser('.')
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  # app.run('localhost', 8080, debug=True)