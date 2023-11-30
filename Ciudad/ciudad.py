from mesa import Agent, Model 
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from typing import Tuple, Any
import numpy as np
import random

def traduccion(val1, val2):
        return val1 - 1, 24 - val2

def traduccion2(val1, val2):
        return val1 + 1, 24 - val2

class Auto(Agent):
    def __init__(self, unique_id, model, origen, destino_or):
        super().__init__(unique_id, model)
        self.next_state = None
        self.unique_id = unique_id
        self.origen = origen
        self.destino_or = destino_or
        self.destino = traduccion(self.destino_or[0], self.destino_or[1])   # Traducción de las coordenadas de destino_or
        self.destino_bool = False
        self.primer_paso = False
        self.direccion = ""
        self.estado = "Inicio"
        self.pos_trad = (self.pos)
        self.llego_a_destino = False
        self.step_quieto = 0 

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
                return direccion # Se queda quieto un segundo, para simular que gira (Aunque no se vea)
        return None # O retorna un valor predeterminado si no encuentra una coincidencia
    
    def girar_con_opciones(self, pos_list, lista_celdas):
        pos_list = tuple(pos_list)
        for coor, dir in lista_celdas:
            if pos_list == coor:
                direccion = random.choice(dir)
                return direccion 
        return None        
    
    def avanza_con_precaucion(self):
        x, y = self.pos
        movimiento = self.movimientos_direccion[self.direccion] # Avanza uno en la dirección del agente
        new_pos = (x + movimiento[0], y + movimiento[1])
        # Si tu siguiente celda no se sale del mapa
        if 0 <= new_pos[0] < self.model.grid.width and 0 <= new_pos[1] < self.model.grid.height:
            # Revisa que hay enfrente
            cell_future = self.model.grid.get_cell_list_contents([new_pos])
            auto_agent = [agent for agent in cell_future if isinstance(agent, Auto)]
            bus_agent = [agent for agent in cell_future if isinstance(agent, Autobus)]

            # Si hay alguien adelante, detente
            if auto_agent or bus_agent:
                self.estado = "Vehiculo enfrente"
                return False
            else:
                # AVANZA
                self.estado = "Avanzando"
                self.model.grid.move_agent(self, new_pos)
                return True
        else:
            # El siguiente paso se sale del mapa
            return False
        

    def step(self):
        x, y = self.pos
        pos_list = [x,y]
        self.pos_trad = traduccion2(x,y)

        # Llegaste a destino
        if tuple(pos_list) == self.destino:
            if self.destino_bool == False:
                self.estado = "Destino"
                self.destino_bool = True
            else:
                # BORRATE
                self.llego_a_destino = True
        else:
            # Revisa que hay donde tu estas
            cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
            estacionamiento_agents = [agent for agent in cell_contents if isinstance(agent, Estacionamiento)]
            semaforo_agents = [agent for agent in cell_contents if isinstance(agent, Semaforo)]
            
            # Si hay un estacionamiento
            if estacionamiento_agents:
                for move in self.movimientos_direccion.values():
                    new_pos = (x + move[0], y + move[1])
                    if self.model.grid.is_cell_empty(new_pos):
                        self.estado = "Saliendo Estacionamiento"
                        self.model.grid.move_agent(self, new_pos)   # SAL
                        pos_list = (pos_list[0] + move[0], pos_list[1] + move[1])
                        self.direccion = self.girar_sin_opcion(pos_list, self.model.list_primeros_traducida) # Toma una dirección
                        break

            # Si ves tu destino
            elif tuple(pos_list) in self.destino_vista_coor:
                pos_list = tuple(pos_list)
                for coor, dir in self.destino_ala_vista:
                    if pos_list == coor:
                        # MIRA
                        posible_mov = self.movimientos_direccion[dir]
                        new_pos = (x + posible_mov[0], y + posible_mov[1])
                        # Revisa que hay delante de ti
                        cell_future = self.model.grid.get_cell_list_contents([(new_pos[0], new_pos[1])])
                        edifico_agent = [agent for agent in cell_future if isinstance(agent, Edificio)]
                        # Si hay una pared mejor sigue como ibas
                        if edifico_agent:
                            self.estado = "vista destino, pared"
                            moved = self.avanza_con_precaucion()
                        # Si no, Avanza hacia el destino
                        else:
                            self.estado = "vista destino, llendo"
                            self.direccion = dir
                            moved = self.avanza_con_precaucion()

            # Si hay un semáforo
            elif semaforo_agents:
                for sema in semaforo_agents:
                    if sema.color == "#FF0200": # Rojo, Alto
                        self.estado = "En semaforo(rojo)"
                        self.model.grid.move_agent(self, (x, y))
                    else:   # Verde, Avanza
                        self.estado = "En semaforo(verde)"
                        moved = self.avanza_con_precaucion()

            # Si hay una vuelta
            elif tuple(pos_list) in self.model.list_giros_coor:
                # Gira
                # Si tu direccion ya es la que deberias tener solo avanza
                if self.direccion == self.girar_sin_opcion(pos_list, self.model.list_giros_t):
                    moved = self.avanza_con_precaucion()
                # Si tienes otra dirección, gira
                # Ya en el siguiente step avanzaras
                else:
                    self.estado = "Girando"
                    self.direccion = self.girar_sin_opcion(pos_list, self.model.list_giros_t)

            # Si hay una decisión
            elif tuple(pos_list) in self.model.list_eleccion_coor:
                # Escoge
                if self.step_quieto == 0:
                    self.step_quieto += 1
                    self.estado = "Girando"
                    self.direccion = self.girar_con_opciones(pos_list, self.model.list_eleccion_t)
                else:
                    self.step_quieto = 0
                    moved = self.avanza_con_precaucion()

            # Si no hay nada de lo anterior, avanza
            else:
                moved = self.avanza_con_precaucion()
                        

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
        self.pos_trad = (self.pos)
        self.step_quieto = 0 
        
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
    
    def avanza_con_precaucion(self):
        x, y = self.pos
        movimiento = self.movimientos_direccion[self.direccion] # Avanza uno en la dirección del agente
        new_pos = (x + movimiento[0], y + movimiento[1])
        # Si tu siguiente celda no se sale del mapa
        if 0 <= new_pos[0] < self.model.grid.width and 0 <= new_pos[1] < self.model.grid.height:
            # Revisa que hay enfrente
            cell_future = self.model.grid.get_cell_list_contents([new_pos])
            auto_agent = [agent for agent in cell_future if isinstance(agent, Auto)]
            bus_agent = [agent for agent in cell_future if isinstance(agent, Autobus)]

            # Si hay alguien adelante, detente
            if auto_agent or bus_agent:
                self.estado = "Vehiculo enfrente"
                return False
            else:
                # AVANZA
                self.estado = "Avanzando"
                self.model.grid.move_agent(self, new_pos)
                return True
        else:
            # El siguiente paso se sale del mapa
            return False

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
                self.estado = "Eligiendo nueva parada..."
                self.indice_parada_actual = (self.indice_parada_actual + 1) % len(self.paradas)
                self.tiempo_parada = 0
        else:
            # Sino, Revisa que hay donde tu estas
            cell_contents = self.model.grid.get_cell_list_contents([(x, y)])
            semaforo_agents = [agent for agent in cell_contents if isinstance(agent, Semaforo)]
            # Si hay un semáforo
            if semaforo_agents:
                for sema in semaforo_agents:
                    if sema.color == "#FF0200": # Rojo, Alto
                        self.estado = "En semaforo(rojo)"
                        self.model.grid.move_agent(self, (x, y))
                    else:   # Verde, Avanza
                        self.estado = "En semaforo(verde)"
                        moved = self.avanza_con_precaucion()
            
            # Si hay una vuelta
            elif tuple(pos_list) in self.model.list_giros_coor:
                # Gira
                # Si tu direccion ya es la que deberias tener solo avanza
                if self.direccion == self.girar_sin_opcion(pos_list, self.model.list_giros_t):
                    moved = self.avanza_con_precaucion()
                # Si tienes otra dirección, gira
                # Ya en el siguiente step avanzaras
                else:
                    self.estado = "Girando"
                    self.direccion = self.girar_sin_opcion(pos_list, self.model.list_giros_t)

            # Si hay una decisión
            elif tuple(pos_list) in self.model.list_eleccion_coor:
                # Escoge
                if self.step_quieto == 0:
                    self.step_quieto += 1
                    self.estado = "Girando"
                    self.direccion = self.girar_con_opciones(pos_list, self.model.list_eleccion_t)
                else:
                    self.step_quieto = 0
                    moved = self.avanza_con_precaucion()
            else:
                moved = self.avanza_con_precaucion()

class Edificio(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.next_state = None

class Estacionamiento(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.next_state = None

class Entrada(Agent):
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
    def __init__(self):
        # Medidas
        ancho = 24
        alto = 24
        # Autos
        numero_autos = 17       # Maximo 17, uno en cada estacionamiento
        numero_autobuses = 1    # Maximo 7, uno en cada parada

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

        lista_entradas: Tuple[Tuple[int, int]] = ( 
            (9,3), (3,4), (18,4), (12,4), (21,4), (6,6),
            (10,9), (22,11), (5,11), (12,10), (17,11),
            (3,18), (19,18), (21,18), (6,20), (9,20), (21,21)
        )

        lista_estacionamientos: Tuple[Tuple[int, int]] = ( 
            (8,3), (3,5), (18,5), (12,5), (21,5), (5,6),
            (9,9), (22,10), (5,10), (12,11), (17,10),
            (3,19), (18,18), (20,18), (6,21), (9,21), (20,21)
        )

        lista_glorietas: Tuple[Tuple[Tuple[int, int], Tuple[int, int]]] = (
            ((14,14),(15,14),(14,15),(15,15)))

        lista_semaforos: Tuple[Tuple[Tuple[int, int], str]] = (
            ((17,1), "V"), ((17,2), "V"), ((15,3), "H"), ((16,3), "H"), ((8,7), "V"), ((8,8), "V"),
            ((6,9), "H"), ((7,9), "H"), ((1,12), "H"), ((2,12), "H"), ((3,13), "V"), ((3,14), "V"),
            ((22,15), "V"), ((22,16), "V"), ((23,17), "H"), ((24,17), "H"), 
            ((15,21), "H"), ((16,21), "H"), ((13,22), "H"), ((14,22), "H"), ((12,23), "V"), ((12,24), "V")
        )

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

        # Coordenadas especiales
        lista_primeros_pasos: Tuple[Tuple[int, int], str] = (
            ((8,2),"Iz"), ((2,5),"Ab"), ((19,5),"Ab"), ((13,5),"Ab"),
            ((20,5),"Ab"),((5,7),"Iz"),

            ((9,8),"Iz"), ((23,10),"Ar"), ((6,10),"Ar"), ((13,11),"Ab"),
            ((16,10),"Ar"), 

            ((2,19),"Ab"), ((18,19),"Iz"), ((20,19),"Iz"), ((7,21),"Ab"),
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

        self.width = ancho
        self.height = alto
        self.num_autos = numero_autos
        self.num_buses = numero_autobuses
        self.list_esta = lista_estacionamientos
        self.list_entr = lista_entradas
        self.list_edif = lista_edificios
        self.list_glor = lista_glorietas
        self.list_sem = lista_semaforos
        self.list_par = lista_paradas
        self.list_alto = lista_alto_autobus
        # self.list_primero = lista_primeros_pasos
        self.list_primeros_traducida = lista_primeros_traducida
        self.list_giros_t = lista_giros_traducida
        self.list_giros_coor = lista_giros_coor
        self.list_eleccion_t = lista_eleccion_traducida
        self.list_eleccion_coor = lista_eleccion_coor



        self.grid = MultiGrid(self.width, self.height, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True # Para la visualizacion usando navegador
        self.num_autos = numero_autos
        self.num_buses = numero_autobuses
        id_agente = 0
        self.autos_destino = 0 

        # Construccion del Mapa

        ## Crea los edificios
        for edificio in self.list_edif:
            rango_x = edificio[1][0] - edificio[0][0] + 1
            rango_y = edificio[1][1] - edificio[0][1] + 1
            for i in range(rango_x):
                for j in range(rango_y):
                    new_edificio = Edificio(id_agente, self)
                    self.grid.place_agent(new_edificio, (traduccion((edificio[0][0] + i), (edificio[0][1] + j))))
                    self.schedule.add(new_edificio)
                    id_agente += 1
        
        ## Glorietas
        for glorieta in self.list_glor:
            new_glorieta = Glorieta(id_agente, self)
            self.grid.place_agent(new_glorieta, (traduccion(glorieta[0], glorieta[1])))
            self.schedule.add(new_glorieta)
            id_agente += 1
        
        ## Semaforos
        for semaforos in self.list_sem:
            X = semaforos[0][0] -1
            Y = self.height - semaforos[0][1]
            new_semaforo = Semaforo(id_agente, self, semaforos[1])
            self.grid.place_agent(new_semaforo, (traduccion(semaforos[0][0], semaforos[0][1])))
            self.schedule.add(new_semaforo)
            id_agente += 1
        
        ## Estacionamientos
        for estacionamiento in self.list_esta:
            new_estacionamiento = Estacionamiento(id_agente, self)
            self.grid.place_agent(new_estacionamiento, (traduccion(estacionamiento[0], estacionamiento[1])))
            self.schedule.add(new_estacionamiento)
            id_agente += 1

        ## Entradas
        for entrada in self.list_entr:
            new_entrada = Entrada(id_agente, self)
            self.grid.place_agent(new_entrada, (traduccion(entrada[0], entrada[1])))
            self.schedule.add(new_entrada)
            id_agente += 1
        
        ## Paradas
        for parada in self.list_par:
            new_parada = Parada(id_agente, self)
            self.grid.place_agent(new_parada, (traduccion(parada[0], parada[1])))
            self.schedule.add(new_parada)
            id_agente += 1
        
        # Vehiculos
        ## Autos
        contador_autos = 0
        for origen_auto in self.list_esta:
            if contador_autos < self.num_autos:

                new_destiny = random.choice([e for e in self.list_entr if e != origen_auto])
                new_auto = Auto(id_agente, self, origen_auto, new_destiny)

                self.grid.place_agent(new_auto, (traduccion(origen_auto[0], origen_auto[1])))
                self.schedule.add(new_auto)
                id_agente += 1
                contador_autos += 1
            else:
                break
        ## Autobuses
        paradas = [parada[0] for parada in self.list_alto]
        direcciones = [direccion[1] for direccion in self.list_alto]
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
        # self.verificar_autos_llegados()   # Descomentar para que el programa termine cuando todos los autos hayan llegado a su destino
        
        # Borrar Agentes que ya llegaron a su destino
        for agente in self.schedule.agents:
            if isinstance(agente, Auto) and agente.llego_a_destino:
                self.remover_agente(agente)

    def verificar_autos_llegados(self):
        autos_destino = sum(1 for agent in self.schedule.agents if isinstance(agent, Auto) and agent.destino_bool)
        if autos_destino == self.num_autos:  #Cuando todos los autos lleguen a su destino termina el programa
            self.running = False
            print("Todos los autos han llegado a su destino!!!")

    def remover_agente(self, agente):
        self.schedule.remove(agente)
        self.grid.remove_agent(agente)
    
    def posicionesAgentes(self):
        result = {"autos": []}
        for agent in self.schedule.agents:
            if isinstance(agent, Auto):
                if agent.estado == "Saliendo Estacionamiento":  # JSON cuando de primeros pasos
                    result["autos"].append({ "ID": agent.unique_id, "Origen": agent.pos,
                                            "Direccion": agent.direccion, "AltoSiguiente": agent.estado})
                elif agent.estado == "Vehiculo enfrente":       # JSON cuando detecte un coche enfrente
                    result["autos"].append({ "ID": agent.unique_id, "Origen": agent.pos,
                                            "Direccion": agent.direccion, "AltoSiguiente": agent.estado})
                elif agent.estado == "En semaforo(rojo)":       # JSON cuando detecte un semáforo
                    result["autos"].append({ "ID": agent.unique_id, "Origen": agent.pos,
                                            "Direccion": agent.direccion, "AltoSiguiente": agent.estado})
                elif agent.estado == "Destino":                 # JSON cuando llegue al destino
                    result["autos"].append({ "ID": agent.unique_id, "Origen": (0,0),
                                            "Direccion": agent.direccion, "AltoSiguiente": agent.estado})
                else:                                       # en movimiento 
                    result["autos"].append({"ID": agent.unique_id})
        return result

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
    elif isinstance(agent, Entrada):
        portrayal = {"Shape": "rect",
                    "Filled": "true",
                    "Layer": 0,
                    "Color": "#00fff7",
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
            info.append(f"Auto ID: {agent.unique_id}, Origen: {agent.origen} Destino: {agent.destino_or}, Posición: {agent.pos_trad}, Estado: {agent.estado}, Dirección: {agent.direccion}")
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
