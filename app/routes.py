from app import app
from app import prenoms

from flask import request
from flask import json

print("--> Reading first names file from 1900 to 2015 (takes time).")
d = prenoms.read_prenom_file('assets/dpt2016.txt')
print("--> Done!")

@app.route('/')
@app.route('/index')
def index():
    
    prenom = request.args.get('firstname')
    depuis = 1900
    sexe = request.args.get('sex')

    print("--> Scoring {}".format('Arnaud'))
    error = None
    try:
        p = prenoms.score(d, prenom, sexe, depuis).to_json(orient='table')
    except Exception as inst:
        error = inst
		
    if error == None:
        response = app.response_class(
            response=json.dumps(p),
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
