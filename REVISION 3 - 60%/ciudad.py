from mesa import Agent, Model 
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from typing import Tuple, Any
import numpy as np
import random

def traduccion(val1, val2):
    return val1 - 1, alto - val2

def trad_2(val1, val2):
    return val1 +1, alto - val2 

class Auto(Agent):
    def __init__(self, unique_id, model, destino_or):
        super().__init__(unique_id, model)
        self.next_state = None
        self.unique_id = unique_id
        self.destino_or = destino_or
        self.destino = traduccion(self.destino_or[0], self.destino_or[1])   # Traducción de las coordenadas de destino_or
        self.destino_bool = False
        self.primer_paso = False
        self.estado = ""
        self.funcion = ""
        self.pos_trad = (self.pos)

        self.destino_ala_vista = (
                ((self.destino[0], self.destino[1] + 1), "Ab"),   # Arriba
                ((self.destino[0], self.destino[1] - 1), "Ar"),   # Abajo
                ((self.destino[0] - 1, self.destino[1]), "De"),   # Izquierda
                ((self.destino[0] + 1, self.destino[1]), "Iz"),   # Derecha
                ((self.destino[0], self.destino[1] + 2), "Ab"),   # Arriba 2
                ((self.destino[0], self.destino[1] - 2), "Ar"),   # Abajo 2
                ((self.destino[0] - 2, self.destino[1]), "De"),   # Izquierda 2
                ((self.destino[0] + 2, self.destino[1]), "Iz"),   # Derecha 2
        )
        self.destino_vista_coor = tuple(tupla[0] for tupla in self.destino_ala_vista)

        self.movimientos_estado = {
            "Ar": (0, 1),   # Arriba
            "Ab": (0, -1),  # Abajo
            "Iz": (-1, 0),  # Izquierda
            "De": (1, 0),   # Derecha
        }

    def girar_sin_opcion(self, pos_list, lista_celdas):
        pos_list = tuple(pos_list)
        for coor, direccion in lista_celdas:
            if pos_list == coor:
                return direccion # Se queda quieto un segundo, para simular que gira (Aunque no se vea)
        return None # O retorna un valor predeterminado si no encuentra una coincidencia
    
    def girar_con_opciones(self, pos_list, lista_celdas):
        pos_list = tuple(pos_list)
        for coor, dir in lista_celdas:
            if pos_list == coor:
                direccion = random.choice(dir)
                return direccion 
        return None        
    
    def step(self):
        x, y = self.pos
        pos_list = [x,y]
        self.pos_trad = (trad_2(x,y))

        if tuple(pos_list) == self.destino:
            if (self.destino_bool == False):
                print(f"LLEGUÉ A MI DESTINO!!!, Auto ID = {self.unique_id}")
                self.funcion = "Destino"
                self.destino_bool = True
        
         # Primero, vemos si esta en un estacionamiento que no sea el de destino       
        else:  
            cell_contents = self.model.grid.get_cell_list_contents([(x, y)])    # Revisa que hay en su celda
            estacionamiento_agents = [agent for agent in cell_contents if isinstance(agent, Estacionamiento)]  # Revisa si hay un estacionamiento en su celda
            semaforo_agents = [agent for agent in cell_contents if isinstance(agent, Semaforo)]
            
            # Si esta en un estacionamiento
            if estacionamiento_agents:
                for move in self.movimientos_estado.values():
                    new_pos = (x + move[0], y + move[1])
                    if self.model.grid.is_cell_empty(new_pos):
                        self.model.grid.move_agent(self, new_pos)
                        self.funcion = "Estacionamiento"
                        break

            # Si ya salio del estacionamiento, da su primer paso
            elif self.primer_paso == False:
                self.estado = self.girar_sin_opcion(pos_list, lista_primeros_traducida)
                self.funcion = "Primer Paso"
                self.primer_paso = True
            
            else:
                movimiento = self.movimientos_estado[self.estado]
                new_pos = (x + movimiento[0], y + movimiento[1])
                if 0 <= new_pos[0] < self.model.grid.width and 0 <= new_pos[1] < self.model.grid.height:
                    cell_future = self.model.grid.get_cell_list_contents([new_pos])
                    auto_agent = [agent for agent in cell_future if isinstance(agent, Auto)]
                    bus_agent = [agent for agent in cell_future if isinstance(agent, Autobus)]

                    # si encuentra otro vehiculo, Alto
                    if auto_agent or bus_agent:
                        self.funcion = "Vehiculo enfrente"
                        self.model.grid.move_agent(self, (x, y))
                    
                    # Si encuentra un semaforo
                    elif semaforo_agents:
                        for sema in semaforo_agents:
                            if sema.color == "#FF0200": # Rojo, Alto
                                self.funcion = "En semaforo(rojo)"
                                self.model.grid.move_agent(self, (x, y))
                            elif sema.color == "#00B050": # Verde, Siga
                                self.funcion = "En semaforo(verde)"
                                movimiento = self.movimientos_estado[self.estado]
                                self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))

                    else:   
                        # Si vé su destino ve hacia el
                        if tuple(pos_list) in self.destino_vista_coor:
                            pos_list = tuple(pos_list)
                            for coor, direccion in self.destino_ala_vista:
                                if pos_list == coor:
                                    movimiento = self.movimientos_estado[direccion]
                                    new_pos = (x + movimiento[0], y + movimiento[1])

                                    # Si ya ves tu destino y no hay nada enmedio, ve hacia el
                                    if self.model.grid.is_cell_empty(new_pos):
                                        self.funcion = "vista destino (1)"
                                        self.estado = direccion
                                        movimiento = self.movimientos_estado[self.estado]
                                        self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))
                                    else:
                                        # Hay algo entre tu destino y tu, que es?
                                        cell_future = self.model.grid.get_cell_list_contents([(new_pos[0], new_pos[1])])
                                        edifico_agent = [agent for agent in cell_future if isinstance(agent, Edificio)]
                                        estacionamiento_agents = [agent for agent in cell_future if isinstance(agent, Estacionamiento)]
                                        # Si es tu destino ve!!!
                                        if estacionamiento_agents and new_pos == self.destino:
                                            self.funcion = "vista destino (2)"
                                            self.estado = direccion
                                            movimiento = self.movimientos_estado[self.estado]
                                            self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))
                                        # Si es una pared de un edificio mejor sigue caminando
                                        elif edifico_agent:
                                            self.funcion = "vista destino (3)"
                                            movimiento = self.movimientos_estado[self.estado]
                                            self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))
                                        
                        # Si esta en una celda de giro
                        elif tuple(pos_list) in lista_giros_coor:
                            self.funcion = "celda de giro"
                            self.estado = self.girar_sin_opcion(pos_list, lista_giros_traducida)    # Cambiamos el estado
                            movimiento = self.movimientos_estado[self.estado]
                            self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))
                        
                        # Si esta en una celda de elección
                        elif tuple(pos_list) in lista_eleccion_coor:
                            self.funcion = "celda de eleccion"
                            self.estado = self.girar_con_opciones(pos_list, lista_eleccion_traducida)
                            movimiento = self.movimientos_estado[self.estado]
                            self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))
                        
                        # Muevete segun tu estado
                        else:
                            if self.estado in self.movimientos_estado:
                                self.funcion = "Avanzando"
                                movimiento = self.movimientos_estado[self.estado]
                                self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))
                else:
                    # Si esta en una celda de giro
                    if tuple(pos_list) in lista_giros_coor:
                        self.funcion = "celda de giro"
                        self.estado = self.girar_sin_opcion(pos_list, lista_giros_traducida)    # Cambiamos el estado
                        movimiento = self.movimientos_estado[self.estado]
                    
                    # Si esta en una celda de elección
                    elif tuple(pos_list) in lista_eleccion_coor:
                        self.funcion = "celda de eleccion"
                        self.estado = self.girar_con_opciones(pos_list, lista_eleccion_traducida)
                        movimiento = self.movimientos_estado[self.estado]

class Autobus(Agent):
    def __init__(self, unique_id, model, direccion, paradas, n_parada):
        super().__init__(unique_id, model)
        self.next_state = None
        self.unique_id = unique_id
        self.paradas = paradas
        self.indice_parada_actual = n_parada
        self.tiempo_parada = 0
        self.tiempo_max_parada = 10
        self.direccion = direccion
        self.estado = "Inicio"
        self.semaforo_verde = False
        self.ya_elegi = False
        self.ya_gire = False
        self.pos_trad = (self.pos)
        
        self.movimientos_direccion = {
            "Ar": (0, 1),   # Arriba
            "Ab": (0, -1),  # Abajo
            "Iz": (-1, 0),  # Izquierda
            "De": (1, 0),   # Derecha
        }

    def girar_sin_opcion(self, pos_list, lista_celdas):
        pos_list = tuple(pos_list)
        for coor, direccion in lista_celdas:
            if pos_list == coor:
                return direccion
        return None
    
    def girar_con_opciones(self, pos_list, lista_celdas):
        pos_list = tuple(pos_list)
        for coor, dir in lista_celdas:
            if pos_list == coor:
                direccion = random.choice(dir)
                return direccion 
        return None 

    def step(self):
        x, y = self.pos
        pos_list = [x,y]
        parada_actual = self.paradas[self.indice_parada_actual]

        # Llegaste a una parada
        if pos_list == parada_actual:
            # Espera en la parada
            if self.tiempo_parada < self.tiempo_max_parada:
                self.estado = "Parada"
                self.tiempo_parada += 1
            # Ahora selecciona otra parada 
            else:
                self.indice_parada_actual = (self.indice_parada_actual + 1) % len(self.paradas)
                self.estado = "Eligiendo nueva parada..."
                self.tiempo_parada = 0
        else:
            # Si tu siguiente celda no se sale del mapa
            movimiento = self.movimientos_direccion[self.direccion]
            new_pos = (x + movimiento[0], y + movimiento[1])
            if 0 <= new_pos[0] < self.model.grid.width and 0 <= new_pos[1] < self.model.grid.height:
                
                # Revisa que hay enfrente
                cell_future = self.model.grid.get_cell_list_contents([new_pos])
                auto_agent = [agent for agent in cell_future if isinstance(agent, Auto)]
                bus_agent = [agent for agent in cell_future if isinstance(agent, Autobus)]
                # Si hay alguien adelante, detente
                if auto_agent or bus_agent:
                    self.estado = "Vehiculo enfrente"
                    self.model.grid.move_agent(self, (x, y))

                else:
                    # Sino, Revisa que hay donde tu estas
                    cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
                    semaforo_agents = [agent for agent in cell_contents if isinstance(agent, Semaforo)]
                    # Si hay un semáforo
                    if semaforo_agents and self.semaforo_verde == False:
                        for sema in semaforo_agents:
                            if sema.color == "#FF0200": # Rojo, Alto
                                self.estado = "En semaforo(rojo)"
                                self.model.grid.move_agent(self, (x, y))
                            else:
                                self.semaforo_verde = True
                    # Si hay una vuelta y no has girado
                    elif tuple(pos_list) in lista_giros_coor and self.ya_gire == False:
                        # Si tu dirección es diferente a la que tiene, gira
                        if self.direccion != self.girar_sin_opcion(pos_list, lista_giros_traducida):
                            self.estado = "celda de giro"
                            self.direccion = self.girar_sin_opcion(pos_list, lista_giros_traducida)
                            self.ya_gire = True
                    # Si hay una decisión y no has decidido
                    elif tuple(pos_list) in lista_eleccion_coor and self.ya_elegi == False:
                        self.estado = "celda de eleccion"
                        self.direccion = self.girar_con_opciones(pos_list, lista_eleccion_traducida)
                        self.ya_elegi = True
                    # Si no hay nada de lo anterior, avanza
                    else:
                        self.ya_gire = False
                        self.ya_elegi = False
                        self.estado = "Avanzando"
                        movimiento = self.movimientos_direccion[self.direccion]
                        self.model.grid.move_agent(self, (x + movimiento[0], y + movimiento[1]))
            else:
                # Si hay una vuelta, gira
                if tuple(pos_list) in lista_giros_coor:
                    self.estado = "celda de giro"
                    self.direccion = self.girar_sin_opcion(pos_list, lista_giros_traducida)
                # Si hay una decisión, escoge
                elif tuple(pos_list) in lista_eleccion_coor:
                    self.estado = "celda de eleccion"
                    self.direccion = self.girar_con_opciones(pos_list, lista_eleccion_traducida)

class Edificio(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.next_state = None

class Estacionamiento(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.next_state = None

class Glorieta(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.next_state = None

class Parada(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.next_state = None

class Semaforo(Agent):
    def __init__(self, unique_id, model, orientacion):
        super().__init__(unique_id, model)
        self.next_state = None
        self.orientacion = orientacion
        self.steps = 0
        if self.orientacion == 'V':
            self.color = "#00B050"  # Verde 
        else:
            self.color = "#FF0200"  # Rojo

    def step(self):
        self.steps += 1
        if self.steps % 10 == 0:
            if self.color == "#00B050":
                self.color = "#FF0200"
            else:
                self.color = "#00B050"

class CiudadModel(Model):
    def __init__(self, width, height, num_autos, list_edif, list_esta, list_glor, list_sem, num_buses,list_par, list_alto):
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True # Para la visualizacion usando navegador
        self.num_autos = num_autos
        self.num_buses = num_buses
        id_agente = 0
        self.autos_destino = 0 

        # Construccion del Mapa

        ## Edificios
        for edificio in list_edif:
            rango_x = edificio[1][0] - edificio[0][0] + 1
            rango_y = edificio[1][1] - edificio[0][1] + 1
            for i in range(rango_x):
                for j in range(rango_y):
                    new_edificio = Edificio(id_agente, self)
                    self.grid.place_agent(new_edificio, (traduccion((edificio[0][0] + i), (edificio[0][1] + j))))
                    self.schedule.add(new_edificio)
                    id_agente += 1
        
        ## Glorietas
        for glorieta in list_glor:
            new_glorieta = Glorieta(id_agente, self)
            self.grid.place_agent(new_glorieta, (traduccion(glorieta[0], glorieta[1])))
            self.schedule.add(new_glorieta)
            id_agente += 1
        
        ## Semaforos
        for semaforos in list_sem:
            X = semaforos[0][0] -1
            Y = height - semaforos[0][1]
            new_semaforo = Semaforo(id_agente, self, semaforos[1])
            self.grid.place_agent(new_semaforo, (traduccion(semaforos[0][0], semaforos[0][1])))
            self.schedule.add(new_semaforo)
            id_agente += 1
        
        ## Estacionamientos
        for estacionamiento in list_esta:
            new_estacionamiento = Estacionamiento(id_agente, self)
            self.grid.place_agent(new_estacionamiento, (traduccion(estacionamiento[0], estacionamiento[1])))
            self.schedule.add(new_estacionamiento)
            id_agente += 1
        
        ## Paradas
        for parada in list_par:
            new_parada = Parada(id_agente, self)
            self.grid.place_agent(new_parada, (traduccion(parada[0], parada[1])))
            self.schedule.add(new_parada)
            id_agente += 1
        
        # Vehiculos
        ## Autos
        contador_autos = 0
        for coche in list_esta:
            if contador_autos < self.num_autos:
                new_destiny = random.choice([e for e in list_esta if e != coche])
                new_auto = Auto(id_agente, self, new_destiny)
                self.grid.place_agent(new_auto, (traduccion(coche[0], coche[1])))
                self.schedule.add(new_auto)
                id_agente += 1
                contador_autos += 1
            else:
                break
        ## Autobuses
        paradas = [parada[0] for parada in list_alto]
        direcciones = [direccion[1] for direccion in list_alto]
        for bus in range(self.num_buses):
                numero_parada = i % len(paradas)    # En que indice de parada nacera
                parada_autobus = paradas[numero_parada]
                direccion_autobus = direcciones[i]
                new_bus = Autobus(id_agente, self, direccion_autobus, paradas, numero_parada)
                self.grid.place_agent(new_bus, (traduccion(parada_autobus[0], parada_autobus[1])))
                self.schedule.add(new_bus)
                id_agente += 1

    def step(self):
        # Hacer avanzar el modelo
        self.schedule.step()
        self.verificar_autos_llegados()

    def verificar_autos_llegados(self):
        autos_destino = sum(1 for agent in self.schedule.agents if isinstance(agent, Auto) and agent.destino_bool)
        if autos_destino == self.num_autos:  #Cuando todos los autos lleguen a su destino termina el programa
            self.running = False
            print("Todos los autos han llegado a su destino!!!")

def agent_portrayal(agent):
    if isinstance(agent, Auto):
        portrayal = {"Shape": "circle",
                        "Filled": "true",
                        "Layer": 1,
                        "Color": "black",
                        "r": 0.8,
                        "text": agent.unique_id
                        }
    elif isinstance(agent, Autobus):
        portrayal = {"Shape": "circle",
                        "Filled": "true",
                        "Layer": 1,
                        "Color": "Orange",
                        "r": 0.8,
                        "text": agent.unique_id
                        }
    elif isinstance(agent, Edificio):
        portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "#5B9BD5",
                    "w": 1,
                    "h": 1
                    }
    elif isinstance(agent, Estacionamiento):
        portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "#FFFF00",
                    "w": 1,
                    "h": 1
                    }
    elif isinstance(agent, Glorieta):
        portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "#833C0B",
                    "w": 1,
                    "h": 1
                    }
    elif isinstance(agent, Semaforo):
        if agent.orientacion == 'H':
            portrayal = {"Shape": "rect",
                        "Filled": "true",
                        "Layer": 0,
                        "Color": agent.color,
                        "w": 1,
                        "h": 1
                        }
        elif agent.orientacion == 'V':
            portrayal = {"Shape": "rect",
                        "Filled": "true",
                        "Layer": 0,
                        "Color": agent.color,
                        "w": 1,
                        "h": 1
                        }
    elif isinstance(agent, Parada):
        portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "#FFC90E",
                    "w": 1,
                    "h": 1
                    }
    else:
        portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "black",
                    "w": 1,
                    "h": 1}
    return portrayal

def get_auto_info(model):
    info = []
    for agent in model.schedule.agents:
        if isinstance(agent, Auto):
            info.append(f"Auto ID: {agent.unique_id},  Destino: {agent.destino_or}, Posición: {agent.pos_trad}, Dirección: {agent.estado}, Estado: {agent.funcion}")
        elif isinstance(agent, Autobus):
            info.append(f"Autobus ID: {agent.unique_id},  Parada: {agent.indice_parada_actual}, Posición: {agent.pos_trad}, Dirección: {agent.direccion}, Estado: {agent.estado}")
    return info

class AutoInfoText(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        info = get_auto_info(model)
        info_html = ''.join([f'<div>{line}</div> <div>&nbsp;</div>' for line in info])
        return f'<div style="position: absolute; top: 70px; left: 10px; max-width: 300px; overflow: hidden; text-overflow: ellipsis;">{info_html}</div>'

if __name__ == "__main__":
    # Medidas
    ancho = 24
    alto = 24

    # Mapa
    lista_edificios: Tuple[Tuple[Tuple[int, int], Tuple[int, int]]] = (
        ((3,3),(12,6)),
        ((17,3),(18,6)),
        ((21,3),(22,6)), 
        
        ((3,9),(5,12)),
        ((8,9),(12,12)),
        ((17,9),(18,12)),
        ((21,9),(22,12)),

        ((3,17),(6,22)),
        ((9,17),(12,22)),
        ((17,17),(22,18)),
        ((17,21),(22,22))
    )

    lista_estacionamientos: Tuple[Tuple[int, int]] = ( 
        (10,3), (3,4), (18,4), (12,5), (21,5), (7,6),
        (9,9), (22,10), (5,11), (12,11), (17,11),
        (3,18), (18,18), (20,18), (6,21), (9,21), (20,21)
    )

    lista_glorietas: Tuple[Tuple[Tuple[int, int], Tuple[int, int]]] = (
        ((14,14),(15,14),(14,15),(15,15))
    )

    lista_semaforos: Tuple[Tuple[Tuple[int, int], str]] = (
        ((17,1), "V"), ((17,2), "V"), ((15,3), "H"), ((16,3), "H"), ((8,7), "V"), ((8,8), "V"),
        ((6,9), "H"), ((7,9), "H"), ((1,12), "H"), ((2,12), "H"), ((3,13), "V"), ((3,14), "V"),
        ((22,15), "V"), ((22,16), "V"), ((23,17), "H"), ((24,17), "H"), 
        ((15,21), "H"), ((16,21), "H"), ((13,22), "H"), ((14,22), "H"), ((12,23), "V"), ((12,24), "V")
    )

    # Coordenadas especiales
    lista_primeros_pasos: Tuple[Tuple[int, int], str] = (
        ((10,2),"Iz"), ((2,4),"Ab"), ((19,4),"Ab"), ((13,5),"Ab"),
        ((20,5),"Ab"),((7,7),"Iz"),

        ((9,8),"Iz"), ((23,10),"Ar"), ((6,11),"Ar"), ((13,11),"Ab"),
        ((16,11),"Ar"), 

        ((2,18),"Ab"), ((18,19),"Iz"), ((20,19),"Iz"), ((7,21),"Ab"),
        ((8,21),"Ab"), ((20,20),"Iz")
    )
    lista_primeros_traducida = tuple((traduccion(tupla[0][0], tupla[0][1]), tupla[1]) for tupla in lista_primeros_pasos)

    lista_celdas_giro: Tuple[Tuple[int, int], str] = (
        ((1,1),"Ab"), ((2,2),"Ab"),
        ((1,7),"Ab"), ((2,8),"Ab"),
        ((1,24),"De"), ((2,23),"De"),

        ((7,24),"De"), ((8,23),"De"),
        ((23,23),"Ar"), ((24,24),"Ar"),
        ((15,20),"Ar"), ((16,19),"Ar"),

        ((23,15),"Ar"), ((24,16),"Ar"),
        ((23,7),"Ar"), ((24,8),"Ar"),
        
        ((23,2),"Iz"), ((24,1),"Iz"),
        ((16,1),"Iz"), ((15,2),"Iz"),

        ((1,13),"Ab"), ((2,14),"Ab"),
        ((6,8),"Iz"), ((7,7),"Iz"),

        ((13,24),"De"), ((14,23),"De"),

        ((19,7),"De"), ((20,8),"De"),
        ((19,8),"De"), ((20,7),"De"),

        ((14,13),"Iz"), 
        ((13,15),"Ab"),
        ((15,16),"De"), 
        ((16,14),"Ar"),
    )
    lista_giros_traducida = tuple((traduccion(tupla[0][0], tupla[0][1]), tupla[1]) for tupla in lista_celdas_giro) # La traducimos segun como Mesa la crea
    lista_giros_coor = tuple(traduccion(tupla[0][0], tupla[0][1]) for tupla in lista_celdas_giro) # Y sacamos unicamente sus coordenadas, para asi estar revisnado si estamos o no en una celda de giro

    lista_celdas_eleccion: Tuple[Tuple[int, int], Tuple[str, str]] = (
        ((1,16), ("Ab","De")), ((2,15), ("Ab", "De")),
        ((6,14), ("Ar","Iz")), ((7,13), ("Ar", "Iz")),
        ((7,16), ("Ab","De")), ((8,15), ("Ab", "De")),
        
        ((13,1), ("Ab","Iz")), ((14,2), ("Ab", "Iz")),
        ((13,7), ("Ab","Iz")), ((14,8), ("Ab", "Iz")),

        ((15,7), ("Ar","De")), ((16,8), ("Ar", "De")),
        ((15,23),("Ar","De")), ((16,24),("Ar", "De")),

        ((19,1), ("Ab","Iz")), ((20,2), ("Ab", "Iz")),
        ((19,14),("Ar","Iz")), ((20,13),("Ar", "Iz")),

        ((23,14),("Ar","Iz")), ((24,13),("Ar", "Iz")),
        ((23,20), ("Ar","Iz")), ((24,19), ("Ar", "Iz")),

        ((13,13), ("Ab","Iz")),
        ((13,16),("Ab", "De")),
        ((16,13), ("Ar","Iz")),
        ((16,16),("Ar", "De"))
    )
    lista_eleccion_traducida = tuple((traduccion(tupla[0][0], tupla[0][1]), tupla[1]) for tupla in lista_celdas_eleccion) # La traducimos segun como Mesa la crea
    lista_eleccion_coor = tuple(traduccion(tupla[0][0], tupla[0][1]) for tupla in lista_celdas_eleccion)

    # Autobuses
    # Lista de paradas que saldran en el Mapa
    lista_paradas: Tuple[Tuple[int, int]] = ( 
        (3,21), (5,3), (9,12), (10,6), (20,17), (21,22), (22,4)
    )

    # Lista de coordenadas donde el autobus se detendra un momento
    lista_alto_autobus: Tuple[Tuple[int, int], str] = ( 
        ((2,21), "Ab"), ((5,2), "Iz"), ((9,13), "Iz"), 
        ((10,7), "Iz"), ((20,16), "De"), ((21,23), "De"), 
        ((23,4), "Ar")
    )

    # Autos
    numero_autos = 7        # Maximo 17, uno en cada estacionamiento
    numero_autobuses = 0    # Maximo 7, uno en cada parada

    info_text = AutoInfoText()
    grid = CanvasGrid(agent_portrayal, ancho, alto, 720, 720)
    server = ModularServer(CiudadModel,
                        [grid, info_text],
                        "Ciudad Model",
                        {"width": ancho, "height": alto, 
                        "num_autos": numero_autos,
                        "list_edif": lista_edificios,
                        "list_esta": lista_estacionamientos,
                        "list_glor": lista_glorietas,
                        "list_sem": lista_semaforos,
                        "num_buses": numero_autobuses,
                        "list_par": lista_paradas,
                        "list_alto": lista_alto_autobus})
    server.port = 8521 # The default
    server.launch()


# Todo 
# Autobuses