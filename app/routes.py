# coding: utf8
from app import app
from app import prenoms

from flask import request
from flask import json

import json

print("--> Reading first names file from 1900 to 2015 (takes time).")
d = prenoms.read_prenom_file('assets/dpt2016.txt')
print("--> Done!")

@app.route('/')
@app.route('/index')
def index():
    
    prenom = request.args.get('firstname')
    depuis = 1900
    sexe = request.args.get('sex')
    excludes = json.loads(request.args.get('excludes'))

    print("--> Scoring {}".format(prenom))
    error = None
    try:
        p = prenoms.score_filter(d, prenom, sexe, depuis, excludes) \
                   .to_json(orient='table')
    except Exception as inst:
        error = inst
		
    if error == None:
        response = app.response_class(
            response=json.dumps(p, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    else:
        response = app.response_class(
            response=json.dumps(json.loads('{"error": "' + repr(error) + '"}')),
            status=500,
            mimetype='application/json'
        )
    return response
