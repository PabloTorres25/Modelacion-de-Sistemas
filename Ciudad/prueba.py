from flask import Flask, redirect, url_for, request
from mesa import Agent, Model 
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from typing import Tuple, Any
import numpy as np
import random
import json
from ciudad import CiudadModel, agent_portrayal, AutoInfoText

#  10.48.80.154
app = Flask(__name__)
@app.route('/informacionAgente', methods=['GET', 'POST'])

def informacionAgente():
    if request.method == 'POST':
        # numPos = request.post['count']
        modelo.step()
        return 'algo'
    elif request.method == 'GET':
        modelo.step()
        positions = modelo.posicionesAgentesCoche()
        return positions

if __name__ == "__main__":
    # modelo = CiudadModel()
    
    # modelo.step()
    # modelo.step()
    # positions = modelo.posicionesAgentesCoche()
    # print(positions)

    # app.run(debug = True)


    info_text = AutoInfoText()
    grid = CanvasGrid(agent_portrayal, 24, 24, 720, 720)
    server = ModularServer(CiudadModel,
                        [grid, info_text],
                        "Ciudad Model")
    server.port = 8521 # The default
    server.launch()