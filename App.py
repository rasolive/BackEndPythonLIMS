#!/usr/bin/python

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

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
        return render_template('index.htm')



@app.route("/Grafico", methods= ['GET', 'POST'])
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
             

        
@app.route("/plot_2", methods= ['GET', 'POST'])
def plot_2():
                df = px.data.gapminder()
                fig = px.scatter(df.query("year==2007"), x="gdpPercap", y="lifeExp",
                        size="pop", color="continent",
                        hover_name="country", log_x=True, size_max=60)
                fig.update_layout(width=700, height=400)
                plot_2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                return plot_2

@app.route("/matplot.png/<rang>")
def plot_svg(rang):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        x_points = range(int(rang))
        axis.plot(x_points, [random.randint(1, 30) for x in x_points])

        output = io.BytesIO()
        FigureCanvasAgg(fig).print_png(output)

        return Response(output.getvalue(), mimetype="image/png")       

@app.route("/matplot2.png")
def plot_png():
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.plot([1, 2, 3, 4], [1, 4, 9, 16])

        output = io.BytesIO()
        FigureCanvasAgg(fig).print_png(output)

        return Response(output.getvalue(), mimetype="image/png")

@app.route("/matplot3.png")
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

@app.route("/soma", methods= ['GET', 'POST'])
def soma():
        if request.method == "POST":
                a = float(request.form.get("a"))
                b = float(request.form.get("b"))
                c = float(request.form.get("c"))
                

                x = f' a soma de {a} + {b} + {c} é igual a {a + b + c}'

                return render_template('index.htm',Resposta = x)

if __name__ == '__main__':
    app.run(debug=True)

