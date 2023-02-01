#!/usr/bin/python

from ctypes import alignment
from unittest.mock import patch
from pandas_datareader import data, wb
from datetime import datetime  
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
from flask import Flask, render_template, request, Response
import io
import base64
import matplotlib.pyplot as plt
import os
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import random
import numpy as np
from flask_cors import CORS
from pymongo import MongoClient
from urllib.request import urlopen
import jwt

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient(os.environ.get('CONN_STRING'))
JWT_SECRET = os.environ.get('JWT_SECRET')

def decodeToken(token, JWT_SECRET):
        try:
                decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                return True
        except:
                return False



web_app = Flask(__name__)
CORS(web_app)

@web_app.route("/")
def index():
        return render_template('index.htm')
        
@web_app.route("/statusLotes", methods= ['GET', 'POST'])
def statusLotes():
                token = request.headers.get('Authorization')
                decoded = decodeToken(token, JWT_SECRET)
                if decoded:
                        today = datetime.now()
                        database = os.environ.get('MONGODB_SCHEMA')
                        colection = 'lotes'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        df = pd.DataFrame(list(colection))
                        df['statusLote'][df['validade'] <= str(today)] = 'V'
                        df2 = pd.DataFrame()
                        listaStatusLote = db['listas'].find({'name': "Status Lote"}, {'_id': 0, 'lista': 1})
                        listaStatusLote = pd.DataFrame(list(listaStatusLote))
                        listaStatusLote = pd.DataFrame(list(listaStatusLote['lista'].iat[0]))
                        statusLote = listaStatusLote['chave'].unique().tolist()
                        df2['statusLote'] = listaStatusLote['chave'].unique()
                        df2['quantidade'] = ''

                        for status in statusLote:
                                df2['quantidade'][df2['statusLote'] == status] = len(df['statusLote'][df['statusLote'] == status])
                                df2['statusLote'][df2['statusLote'] == status] = listaStatusLote['valor'][listaStatusLote['chave'] == status].iat[0]

                        fig = px.bar(df2, x="statusLote", y="quantidade", text="quantidade", color='statusLote',
                        labels={
                                        "statusLote": "Status",
                                        "quantidade": "Quantidade de Lotes"
                                        },)
                        fig.update_traces( marker_line_color='rgb(8,48,107)',
                                        marker_line_width=1.5, opacity=0.6, showlegend=False)
                        fig.update_layout(title_text="Status dos Lotes", title_x=0.5)
                        
                        statusLotes = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                        return statusLotes
                else:
                        return {'respone':'token inválido'}

@web_app.route("/statusMateriais", methods= ['GET', 'POST'])
def statusMateriais():
                token = request.headers.get('Authorization')
                decoded = decodeToken(token, JWT_SECRET)
                if decoded:
                        database = os.environ.get('MONGODB_SCHEMA')
                        colection = 'materiais'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        df = pd.DataFrame(list(colection))
                        df2 = pd.DataFrame()
                        listaStatusMaterial = db['listas'].find({'name': "Status Material"}, {'_id': 0, 'lista': 1})
                        listaStatusMaterial = pd.DataFrame(list(listaStatusMaterial))
                        listaStatusMaterial = pd.DataFrame(list(listaStatusMaterial['lista'].iat[0]))
                        statusMaterial= listaStatusMaterial['chave'].unique().tolist()
                        df2['statusMaterial'] = listaStatusMaterial['chave'].unique()
                        df2['quantidade'] = ''
                        for status in statusMaterial:
                                df2['quantidade'][df2['statusMaterial'] == status] = len(df['statusMaterial'][df['statusMaterial'] == status])
                                df2['statusMaterial'][df2['statusMaterial'] == status] = listaStatusMaterial['valor'][listaStatusMaterial['chave'] == status].iat[0]
                        df2
                        fig = px.pie(df2, names="statusMaterial", values="quantidade", hole=.7)

                        # fig = px.bar(df2, x="statusMaterial", y="quantidade", text="quantidade", color='statusMaterial',
                        # labels={
                        #                 "statusMaterial": "Status",
                        #                 "quantidade": "Quantidade de Materiais"
                        #                 },)
                        fig.update_traces( marker_line_color='rgb(8,48,107)',
                                        marker_line_width=1.5, opacity=0.8)
                        fig.update_layout(title_text="Status dos Materiais", title_x=0.5,  legend=dict(
                                                        
                                                        font=dict(size= 10)
                                                        ))
                
                        statusMateriais = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                        return statusMateriais
                else:
                        return {'respone':'token inválido'}

@web_app.route("/userProfiles", methods= ['GET', 'POST'])
def userProfiles():
                token = request.headers.get('Authorization')
                decoded = decodeToken(token, JWT_SECRET)
                if decoded:
                        database = os.environ.get('MONGODB_SCHEMA')
                        colection = 'users'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        df = pd.DataFrame(list(colection))
                        df2 = pd.DataFrame()
                        listaUserProfile = db['listas'].find({'name': "UserProfile"}, {'_id': 0, 'lista': 1})

                        listaUserProfile = pd.DataFrame(list(listaUserProfile))

                        listaUserProfile = pd.DataFrame(list(listaUserProfile['lista'].iat[0]))
                        userProfiles = listaUserProfile['chave'].unique().tolist()
                        df2['userProfiles'] = listaUserProfile['chave'].unique()
                        df2['Perfil'] = listaUserProfile['valor'].unique()
                        df2['Quantidade'] = ''

                        for profile in userProfiles:
                                qtd = 0
                                for linha in df.index:
                                
                                        
                                        res = [x for x in df['role'][linha] if x['perfil'] == profile]
                                        if len(res) > 0:
                                                qtd = qtd + 1

                                df2['Quantidade'][df2['userProfiles'] == profile] = qtd
                        
                        fig = px.line(df2, x="Perfil", y="Quantidade", text="Quantidade")
                        fig.update_layout(title_text="Usuários por Perfil", title_x=0.5)
                        fig.update_traces(textposition="bottom right")
                
                        userProfiles = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                        return userProfiles
                else:
                        return {'respone':'token inválido'}


@web_app.route("/suppliersMaterials", methods= ['GET', 'POST'])
def suppliersMaterials():
                token = request.headers.get('Authorization')
                decoded = decodeToken(token, JWT_SECRET)
                if decoded:
                        database = os.environ.get('MONGODB_SCHEMA')
                        colection = 'suppliers'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        suppliers = pd.DataFrame(list(colection))
                        suppliers = suppliers[['_id', 'name']].drop_duplicates()
                        suppliers['Quantidade'] =''
                        database = os.environ.get('MONGODB_SCHEMA')
                        colection = 'materiais'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        materiais = pd.DataFrame(list(colection))
                        materiais['fornecedor'][1].count(2)
                        for id in suppliers['_id'].to_list():
                                qtd = 0
                                for linha in materiais.index:                  
                                        
                                        res = materiais['fornecedor'][linha].count(id)        
                                        qtd = qtd + res

                                suppliers['Quantidade'][suppliers['_id'] == id] = qtd
                        fig = px.bar(suppliers, x="Quantidade", y="name", orientation='h',labels={
                                        "name": "Fornecedor",
                                        "Quantidade": "Quantidade de materiais"
                                        })
                        fig.update_layout(title_text="Materiais por Fornecedor", title_x=0.5)
                
                        suppliersMaterials = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                        return suppliersMaterials
                else:
                        return {'respone':'token inválido'}


@web_app.route("/fornecedoresMap", methods= ['GET', 'POST'])
def fornecedoresMap():
                token = request.headers.get('Authorization')
                decoded = decodeToken(token, JWT_SECRET)
                if decoded:
                        with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
                                Brazil = json.load(response) # Javascrip object notation 
                        state_id_map = {}
                        for feature in Brazil ['features']:
                                feature['id'] = feature['properties']['name']
                                state_id_map[feature['properties']['sigla']] = feature['id']
                        database = os.environ.get('MONGODB_SCHEMA')
                        colection = 'suppliers'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        df = pd.DataFrame(list(colection))
                        colection = 'estados'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        df2 = pd.DataFrame(list(colection))
                        df2['quantidade'] =''
                        estados = df2['Sigla'].unique().tolist()
                        for estado in estados:
                                df2['quantidade'][df2['Sigla'] == estado] = len(df['estado'][df['estado'] == estado])

                        fig = px.choropleth(
                        df2, #soybean database
                        locations = 'Estado', #define the limits on the map/geography
                        geojson = Brazil, #shape information
                        color = "quantidade", #defining the color of the scale through the database
                        hover_name = 'Estado', #the information in the box
                        hover_data =["quantidade","Longitude","Latitude"],
                        title = "Fornecedores por Estado", #title of the map
                        )
                        fig.update_geos(fitbounds = "locations", visible = True)
                        fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})
                        fig.update_layout(legend=dict(yanchor="bottom", y=0.9, xanchor="right", x=1,
                                                        
                                                font=dict(size= 10)
                                                ))
                        fig.update_traces(showlegend=True)
                        fornecedoresMap = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                        return fornecedoresMap
                else:
                        return {'respone':'token inválido'}


@web_app.route("/prazoValidade", methods= ['GET', 'POST'])
def prazoValidade():
                token = request.headers.get('Authorization')
                decoded = decodeToken(token, JWT_SECRET)
                if decoded:
                        today = datetime.now()
                        database = os.environ.get('MONGODB_SCHEMA')
                        colection = 'lotes'
                        db = client[database]
                        colection = db[colection].find({'active': True})
                        df = pd.DataFrame(list(colection))
                        df['prazoValidade'] = ''
                        df['prazoValidade'][df['validade'] <= str(today + timedelta(days=120))] = '120 dias'
                        df['prazoValidade'][df['validade'] <= str(today + timedelta(days=90))] = '90 dias'
                        df['prazoValidade'][df['validade'] <= str(today + timedelta(days=60))] = '60 dias'
                        df['prazoValidade'][df['validade'] <= str(today + timedelta(days=30))] = '30 dias'
                        df['prazoValidade'][df['validade'] <= str(today)] = ''
                        df2 = pd.DataFrame()
                        listaValidade = ('30 dias', '60 dias', '90 dias', '120 dias')
                        df2['prazoValidade'] = listaValidade
                        df2['quantidade'] = ''
                        for validade in listaValidade:
                                df2['quantidade'][df2['prazoValidade'] == validade] = len(df['prazoValidade'][df['prazoValidade'] == validade])
                        fig = px.bar(df2, x="prazoValidade", y="quantidade", text="quantidade", color='prazoValidade',
                        labels={
                                        "prazoValidade": "Pazo",
                                        "quantidade": "Quantidade de Lotes"
                                        },)
                        fig.update_traces( marker_line_color='rgb(8,48,107)',
                                        marker_line_width=1.5, opacity=0.6, showlegend=False)
                        fig.update_layout(title_text="Lotes a Vencer nos próximos dias", title_x=0.5)
                        prazoValidade = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                        return prazoValidade
                else:
                        return {'respone':'token inválido'}

# @web_app.route("/matplot.png/<rang>")
# def plot_svg(rang):
#         fig = Figure()
#         axis = fig.add_subplot(1, 1, 1)
#         x_points = range(int(rang))
#         axis.plot(x_points, [random.randint(1, 30) for x in x_points])

#         output = io.BytesIO()
#         FigureCanvasAgg(fig).print_png(output)

#         return Response(output.getvalue(), mimetype="image/png")       

# @web_app.route("/matplot2.png")
# def plot_png():
#         fig = Figure()
#         axis = fig.add_subplot(1, 1, 1)
#         axis.plot([1, 2, 3, 4], [1, 4, 9, 16])

#         output = io.BytesIO()
#         FigureCanvasAgg(fig).print_png(output)

#         return Response(output.getvalue(), mimetype="image/png")



if __name__ == '__main__':
    web_app.run(host='0.0.0.0', debug=True, threaded=True)

