from flask import Flask, redirect, url_for, request
from mesa import Agent, Model 
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
import json
from ciudad import CiudadModel, agent_portrayal, AutoInfoText

#  10.48.80.154
app = Flask(__name__)
@app.route('/informacionAgente', methods=['GET', 'POST'])

def informacionAgente():
    if request.method == 'POST':
        return 'Se debe usar Get'
    elif request.method == 'GET':
        modelo.step()
        positions = modelo.posicionesAgentes()
        json_string = json.dumps(positions)
        return json_string

if __name__ == "__main__":
    modelo = CiudadModel()
    # app.run(debug = True)


    # for paso in range(100):
    #     modelo.step()
    #     positions = modelo.posicionesAgentes()
    #     json_string = json.dumps(positions)
    #     print(json_string)
        
    

    info_text = AutoInfoText()
    grid = CanvasGrid(agent_portrayal, 24, 24, 720, 720)
    server = ModularServer(CiudadModel,
                        [grid, info_text],
                        "Ciudad Model")
    server.port = 8521 # The default
    server.launch()