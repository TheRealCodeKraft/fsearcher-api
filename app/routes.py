from app import app
from app import prenoms

from flask import request

@app.route('/')
@app.route('/index')
def index():

    print("--> Reading first names file from 1900 to 2015 (takes time).")
    d = prenoms.read_prenom_file('assets/dpt2016.txt')
    
    prenom = request.args.get('firstname')
    depuis = 1900
    sexe = request.args.get('sex')

    print("--> Scoring {}".format('Arnaud'))
    p = prenoms.score(d, prenom, sexe, depuis).to_json(orient='table')

    return p
