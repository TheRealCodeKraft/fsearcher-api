# coding: utf8
from app import app
from app import prenoms

from flask import request
from flask import json

import json

USE_DB = True

if not USE_DB:
    print("--> Reading first names file from 1900 to 2015 (takes time).")
    d = prenoms.read_prenom_file('assets/dpt2016.txt')
    print("--> Done!")
else:
    d = None

@app.route('/')
@app.route('/index')
def index():
    
    prenom = request.args.get('firstname')
    depuis = 1900
    sexe = request.args.get('sex')
    tt = request.args.get('excludes')
    if tt is not None:
        excludes = json.loads(tt)
    else:
        excludes = None

    print("--> Scoring {}".format(prenom))
    error = None
    try:
        p = prenoms.score_filter(prenom, d, sexe=sexe,
                                 depuis=depuis, exclude=excludes) \
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

@app.route('/favs')
def favs():
    print('Adding favs for [' + request.args.get('uuid') + '] : ' + request.args.get('favs'))
    return app.response_class(
				response=json.dumps(json.loads('{"success": true}')),
				status=200,
				mimetype='application/json'
		)

@app.route('/excludes')
def excludes():
    print('Adding excludes for [' + request.args.get('uuid') + '] : ' + request.args.get('excludes'))
    return app.response_class(
				response=json.dumps(json.loads('{"success": true}')),
				status=200,
				mimetype='application/json'
		)
