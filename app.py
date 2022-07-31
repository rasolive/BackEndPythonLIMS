#!/usr/bin/python

from ctypes import alignment
from unittest.mock import patch
from pandas_datareader import data, wb
import datetime
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

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient('mongodb+srv://m001-student:rasolive0532291@sandbox.wuewv.mongodb.net/lims?retryWrites=true&w=majority')

web_app = Flask(__name__)
CORS(web_app)

@web_app.route("/")
def index():
        return render_template('index.htm')



@web_app.route("/Grafico", methods= ['GET', 'POST'])
def teste():
        
        if request.method == "POST":
               
                body = request.get_json()
                print(body["name"])
                name = body["name"]
                ano = int(body["ano"])
                i = datetime.datetime(ano, 1, 1)
                f = datetime.datetime(2021,1, 22)
                Stock = data.DataReader(name, 'yahoo', i, f)
    
                fig = go.Figure(data=go.Scatter(x= Stock.index, y=Stock["Close"]))
     
                plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            
                return plot_json
             

        
@web_app.route("/statusLotes", methods= ['GET', 'POST'])
def statusLotes():
                database = "lims"
                colection = 'lotes'
                db = client[database]
                colection = db[colection].find()
                df = pd.DataFrame(list(colection))
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

@web_app.route("/statusMateriais", methods= ['GET', 'POST'])
def statusMateriais():
                database = "lims"
                colection = 'materiais'
                db = client[database]
                colection = db[colection].find()
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


@web_app.route("/fornecedoresMap", methods= ['GET', 'POST'])
def fornecedoresMap():
                with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
                        Brazil = json.load(response) # Javascrip object notation 
                state_id_map = {}
                for feature in Brazil ['features']:
                        feature['id'] = feature['properties']['name']
                        state_id_map[feature['properties']['sigla']] = feature['id']
                database = "lims"
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

@web_app.route("/matplot.png/<rang>")
def plot_svg(rang):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        x_points = range(int(rang))
        axis.plot(x_points, [random.randint(1, 30) for x in x_points])

        output = io.BytesIO()
        FigureCanvasAgg(fig).print_png(output)

        return Response(output.getvalue(), mimetype="image/png")       

@web_app.route("/matplot2.png")
def plot_png():
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.plot([1, 2, 3, 4], [1, 4, 9, 16])

        output = io.BytesIO()
        FigureCanvasAgg(fig).print_png(output)

        return Response(output.getvalue(), mimetype="image/png")

@web_app.route("/matplot3.png")
def plot_pngcolormash():
        np.random.seed(19680801)
        Z = np.random.rand(6, 10)
        x = np.arange(-0.5, 10, 1)  # len = 11
        y = np.arange(4.5, 11, 1)  # len = 7

        fig, axis = plt.subplots()
        axis.pcolormesh(x, y, Z)

        # fig = Figure()
        # axis = fig.add_subplot(1, 1, 1)
        # axis.plot([1, 2, 3, 4], [1, 4, 9, 16])

        output = io.BytesIO()
        FigureCanvasAgg(fig).print_png(output)

        return Response(output.getvalue(), mimetype="image/png")  

@web_app.route("/soma", methods= ['GET', 'POST'])
def soma():
        if request.method == "POST":
                a = float(request.form.get("a"))
                b = float(request.form.get("b"))
                c = float(request.form.get("c"))
                

                x = f' a soma de {a} + {b} + {c} é igual a {a + b + c}'

                return render_template('index.htm',Resposta = x)

if __name__ == '__main__':
    web_app.run(host='0.0.0.0', debug=True, threaded=True)

