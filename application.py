import requests
import xmltodict
import pprint
import json

url = "https://bps.quickbase.com/db/bqsuve7qy?a=API_DoQuery&fmt=structured&usertoken=b5d3bm_kn5b_d4c4hh5b76ajm4t6fzg96bbber"
#url = "https://builderprogram-pverma.quickbase.com/db/bqscz87a5?a=API_DoQuery&fmt=structured&ticket=9_bqs7bdfax_b5fdma_nx3z_a_-b_ufsj4vbstivafsmxsfcdxq9mdbckgwuzxb8r9rk9bvnwt8ebi7agah_d2re5rt"

response = requests.request("GET", url)
print(response)
r=response.text.encode('utf8')
print(r)
pp = pprint.PrettyPrinter(indent=4)
data=json.dumps(xmltodict.parse(r))
data1=json.loads(data)
print(data1)

document_url=[]
R_ID=[]
def get_data():
    document_url=[]
    R_ID=[]
    R_Id=Document=""
    for i in data1.values():
        values=i['table']['records']['record']
        for j in values:
            list_data=j['f']
#             print(list_data)
            for data in list_data:
                if data['@id']=="8":
                    Document=data['url']
                    document_url.append(Document)
                if data['@id']=="3":
                    R_Id=data['#text']
                    R_ID.append(R_Id)
#     print(R_ID)
#     print(document_url)
    Mapped_data=dict(zip(R_ID,document_url))
    return Mapped_data


data_all=get_data()
print(data_all)


from zipfile import ZipFile
from urllib.request import urlopen
from io import BytesIO
from zipfile import *
from bs4 import BeautifulSoup
import pandas as pd


for key, value in data_all.items():
    print(value)
#     wordfile=urlopen(value).read()
#     print(wordfile)


track_changed_for_del=[]
track_changed_for_ins=[]
for key, value in data_all.items():
    wordfile=urlopen(value).read()
    wordfile=BytesIO(wordfile)
    document=ZipFile(wordfile)
    document.namelist()
    xml_content=document.read('word/document.xml')
    wordobj=BeautifulSoup(xml_content.decode('utf-8'),'xml')
    key_record=key
    for dl in wordobj.find_all('w:del'):
        Text=dl.text
        author=dl.get('w:author')
        Date=dl.get('w:date')
        Type='Deleted Text'
        ID=dl.get('w:id')
        ID=int(ID)
        dataDict_del = { 'Text':Text,'Author':author,'Date':Date,'Type':Type,'ID':ID,'Record_Id':key_record}
        track_changed_for_del.append(dataDict_del)
    
        
    for ins in wordobj.find_all('w:ins'):
        Text=ins.text
        author=ins.get('w:author')
        Date=ins.get('w:date')
        Type='Inserted Text'
        ID=ins.get('w:id')
        ID=int(ID)
        dataDict_ins = { 'Text':Text,'Author':author,'Date':Date,'Type':Type,'ID':ID,'Record_Id':key_record}
        track_changed_for_ins.append(dataDict_ins)
    df_track_changed_ins= pd.DataFrame(track_changed_for_ins)
    df_track_changed_del= pd.DataFrame(track_changed_for_del)
    df_track_changed_del["Text"]= df_track_changed_del["Text"].replace(' ', "NaN")
    df_track_changed_ins["Text"]= df_track_changed_ins["Text"].replace('', "NaN")
    df_track_changed_del.drop(df_track_changed_del.loc[df_track_changed_del['Text']=='NaN'].index, inplace=True)
    df_track_changed_ins=df_track_changed_ins.sort_values(by='ID')
    df_track_changed_del=df_track_changed_del.sort_values(by='ID')
    

all_data=df_track_changed_ins.append(df_track_changed_del)


all_data=all_data.sort_values(by='ID',ascending=True)

val=all_data.to_dict('records')
csv_data=all_data.to_csv(index=False,header=False)

from flask import Flask,request, render_template, session, redirect

val=all_data.to_dict('records')


import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Create some test data for our catalog in the form of a list of dictionaries.
data=val


@app.route('/', methods=['GET'])
def home():
    return '''<h1>WELCOME</h1>
<p>Get all insterted and delected text from the word document.</p>'''

# A route to return all of the available entries in our catalog.
@app.route('/api/all', methods=['GET'])
def api_all():
    return jsonify(data)

@app.route('/api', methods=['GET'])

def api_id():
    if 'Id' in request.args:
        Id = request.args['Id']
        print(Id)
    else:
        return "Error: No id field provided. Please specify an id."
    results = []
    for d in data:
        if d['Record_Id'] == Id:
            results.append(d)
    return jsonify(results)
    

app.run(debug=True,use_reloader=False)






