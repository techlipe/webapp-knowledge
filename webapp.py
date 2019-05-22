from elasticsearch import Elasticsearch
from flask import Flask,abort, jsonify, request,redirect,url_for
from werkzeug.utils import secure_filename
import json
import os
import requests
from elasticapm.contrib.flask import ElasticAPM


es=Elasticsearch()
UPLOAD_FOLDER = "C:\\Users\Felip\OneDrive\Área de Trabalho\Windows"
ALLOWED_EXTENSIONS = set(['txt'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
apm = ElasticAPM(app, service_name='xupacabra',debug=True)

@app.route('/')
def main():
    return 'main api'

@app.route('/searchdocs')
def searchall():
    doc = {
        'size' : 10000,
        'query': {
            'match_all' : {}
       }
   }
    results= es.search(index='test',body=doc)
    return jsonify(results)

@app.route('/publica', methods=['POST'])
def publica():
    if request.json:
        es=Elasticsearch()
        res=es.index(index='test',doc_type='doc',body=request.json)
        return res['result']
    else:
        return abort(500)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path_file=app.config['UPLOAD_FOLDER']+"\\"+filename
            exists=validaarq(path_file)
            if exists:
                json=montajson(path_file)
                headers= {'content-type': 'application/json'}
                r=requests.post('http://localhost:5000/publica',data=json,headers=headers)
                return str(r.status_code)+str(r.reason)
                
                
                
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

#@app.route('/validaarq',methods=['POST'])
def validaarq(arq):
    exists = os.path.isfile(arq)
    print(exists)
    if exists:
        return exists
    else:
        return exists
    
def montajson(info):
    chaves=['error','description','solution','incident','technology']
    cont=0
    data={}
    with open(info) as param:
        #line=param.readline()
        for line in param:
            print(line,param)
            data[chaves[cont]] = line
            cont+=1
        json_data = json.dumps(data)
        result = "{\"doc\" :"+ json_data +", \"doc_as_upsert\" : true }" 
    return result

