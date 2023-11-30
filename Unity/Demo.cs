using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections.Generic;
using System.Linq;
using System;

public class Demo : MonoBehaviour
{

    // Variables a utilizar
    public GameObject coche1;
    public GameObject coche2;
    public GameObject coche3;
    public GameObject coche4;
    public GameObject coche5;
    private float tiempoTranscurrido;
    public float intervalo; // Intervalo de tiempo en segundos
    private int contador;
    public float velocidadMovimiento;
    public float intervalo10xSeg;
    float progresoTransformacion;
    public bool prueba;

    private string jsonString; // Variable para almacenar el JSON obtenido


    Dictionary<int, DatosPersonalizados> diccionarioAgentes;    // Diccionario para alojar los agentes y sus datos


    // Start is called before the first frame update
    void Start()
    {
        progresoTransformacion = 0.0f;
        tiempoTranscurrido = 0f;
        intervalo = 0.05f;
        contador = 1; // Inicializar el contador para matrices
        diccionarioAgentes = new Dictionary<int, DatosPersonalizados>();
    }

    // Update is called once per frame
    void Update()
    {
        tiempoTranscurrido += Time.deltaTime;

        if (tiempoTranscurrido >= intervalo)
        {
            AccionCadaSegundo();
            MiFuncion();
            tiempoTranscurrido = 0f; // Reinicia el contador de tiempo

        }
    }

    void MiFuncion()
    {
        for (int i = 0; i < 10; i++)
        {
            foreach (KeyValuePair<int, DatosPersonalizados> dato in diccionarioAgentes)
            {
                if (dato.Value.movimiento)
                {
                    dato.Value.z = -0.1f;
                }
                else
                {
                    dato.Value.z = 0;
                }

                if (dato.Value.primeraVezRotando)
                {
                    if (dato.Value.direccionPrimeraVez == "Ar")
                    {
                        dato.Value.aRot = VecOps.RotateY(180);
                        dato.Value.primeraVezRotando = false;
                    }
                    else if (dato.Value.direccionPrimeraVez == "Ab")
                    {
                        dato.Value.aRot = VecOps.RotateY(0);
                        dato.Value.primeraVezRotando = false;
                    }
                    else if (dato.Value.direccionPrimeraVez == "De")
                    {
                        dato.Value.aRot = VecOps.RotateY(-90);
                        dato.Value.primeraVezRotando = false;
                    }
                    else
                    {
                        dato.Value.aRot = VecOps.RotateY(90);
                        dato.Value.primeraVezRotando = false;
                    }
                }
                else
                {
                    if (dato.Value.rotando)
                    {
                        if (dato.Value.direccionVieja == "Ar" && dato.Value.direccionNueva == "Iz" || dato.Value.direccionVieja == "Ab" && dato.Value.direccionNueva == "De"
                            || dato.Value.direccionVieja == "De" && dato.Value.direccionNueva == "Ar" || dato.Value.direccionVieja == "Iz" && dato.Value.direccionNueva == "Ab")
                        {
                            dato.Value.aRot = VecOps.RotateY(-90);
                            dato.Value.rotando = false;
                        }
                        else if (dato.Value.direccionVieja == "Ar" && dato.Value.direccionNueva == "De" || dato.Value.direccionVieja == "Ab" && dato.Value.direccionNueva == "Iz"
                            || dato.Value.direccionVieja == "De" && dato.Value.direccionNueva == "Ab" || dato.Value.direccionVieja == "Iz" && dato.Value.direccionNueva == "Ar")
                        {
                            dato.Value.aRot = VecOps.RotateY(90);
                            dato.Value.rotando = false;
                        }
                        else if (dato.Value.direccionVieja == dato.Value.direccionNueva)
                        {
                            dato.Value.aRot = VecOps.RotateY(0);
                        }
                    }
                    else
                    {
                        dato.Value.aRot = VecOps.RotateY(0);
                    }
                }
                dato.Value.aTrans = VecOps.TranslateM(0, 0, dato.Value.z);
                dato.Value.matrix = dato.Value.currMat * dato.Value.aTrans * dato.Value.aRot * dato.Value.aEscala;
                dato.Value.agenteAuto.GetComponent<MeshFilter>().mesh.vertices = VecOps.ApplyTransform(dato.Value.autoOriginals, dato.Value.matrix).ToArray();
                dato.Value.currMat = dato.Value.currMat * dato.Value.aTrans * dato.Value.aRot;
            }
        }
    }

    void AccionCadaSegundo()
    {
        StartCoroutine(PideDatosGet());
    }

    void CrearAgente(int id, int xC, int zC, string direccion)
    {
        DatosPersonalizados datosAgente = new DatosPersonalizados();
        
        // Crear una instancia de la clase Random
        System.Random rnd = new System.Random();

        // Generar un número aleatorio entre 1 y 5
        int numeroAleatorio = rnd.Next(1, 5);
        
        if(numeroAleatorio == 1)
        {
            datosAgente.agenteAuto = Instantiate(coche1);

        }
        else if(numeroAleatorio == 2)
        {
            datosAgente.agenteAuto = Instantiate(coche2);
        }
        else if (numeroAleatorio == 3)
        {
            datosAgente.agenteAuto = Instantiate(coche3);
        }
        else if (numeroAleatorio == 4)
        {
            datosAgente.agenteAuto = Instantiate(coche4);
        }
        else if (numeroAleatorio == 4)
        {
            datosAgente.agenteAuto = Instantiate(coche5);
        }

        datosAgente.aEscala = VecOps.ScaleM(0.2f, 0.3f, 0.1f);
        datosAgente.autoOriginals = datosAgente.agenteAuto.GetComponent<MeshFilter>().mesh.vertices.ToList();
        datosAgente.agenteAuto.name = id.ToString();


        datosAgente.aTrans = Matrix4x4.identity;
        datosAgente.aRot = Matrix4x4.identity;
        datosAgente.currMat = VecOps.TranslateM(xC, 20.2f, zC);
        //datosAgente.matrix = Matrix4x4.identity;

        datosAgente.z = 0;

        datosAgente.direccionPrimeraVez = direccion;

        datosAgente.movimiento = false;
        datosAgente.rotando = false;
        datosAgente.primeraVezRotando = true;

        diccionarioAgentes.Add(id, datosAgente);
    }





    // Regreso elemento de tipo IEnumerator porque tengo funcionalidad asíncrona
    IEnumerator PideDatosGet()
    {
        using UnityWebRequest www = UnityWebRequest.Get("http://127.0.0.1:5000/informacionAgente");
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            // Salió mal:
            Debug.Log(www.error);
        }
        else
        {
            // Salio bien:
            jsonString = www.downloadHandler.text;

            // Dividir el JSON en un array de strings (cada objeto individual)
            AgentesJson ma = AgentesJson.CreateFromJSON(jsonString);
            foreach (Agente data in ma.autos)
            {
                if (data.AltoSiguiente == "Saliendo Estacionamiento")
                {
                    //Debug.Log("CREATE");
                    CrearAgente(data.ID, data.Origen[0], data.Origen[1], data.Direccion);
                }
                else if (data.AltoSiguiente == "Destino")
                {
                    //Debug.Log("MUERE");
                    GameObject objetoAsociado = diccionarioAgentes[data.ID].agenteAuto;
                    GameObject.Destroy(objetoAsociado);
                    diccionarioAgentes.Remove(data.ID);
                }
                else if (data.AltoSiguiente == "Vehiculo enfrente" || data.AltoSiguiente == "En semaforo(rojo)")
                {
                    //Debug.Log("DETENTE");
                    DatosPersonalizados datosAgente = diccionarioAgentes[data.ID];
                    datosAgente.movimiento = false;
                    datosAgente.rotando = false;
                    datosAgente.direccionVieja = data.Direccion;
                    diccionarioAgentes[data.ID] = datosAgente;
                }
                else if (data.AltoSiguiente == "Girando")
                {
                    //Debug.Log("GIRA:  " + data.ID + "  HACIA LA: "  + data.Direccion);
                    DatosPersonalizados datosAgente = diccionarioAgentes[data.ID];
                    datosAgente.movimiento = false;
                    datosAgente.direccionNueva = data.Direccion;
                    datosAgente.rotando = true;
                    diccionarioAgentes[data.ID] = datosAgente;

                }
                else if (data.AltoSiguiente == "Avanzando")
                {
                    //Debug.Log("Avanza");
                    DatosPersonalizados datosAgente = diccionarioAgentes[data.ID];
                    datosAgente.movimiento = true;
                    datosAgente.rotando = false;
                    datosAgente.direccionVieja = data.Direccion;
                    diccionarioAgentes[data.ID] = datosAgente;
                }

            }
        }
    }
}


// Clase que tiene todos los datos de cada agente
public class DatosPersonalizados
{
    public GameObject agenteAuto;

    public List<Vector3> autoOriginals;

    public Matrix4x4 matriz;
    public Matrix4x4 currMat;
    public Matrix4x4 matrix;
    public Matrix4x4 aTrans;
    public Matrix4x4 aRot;
    public Matrix4x4 aEscala;


    public float z;

    public string direccionNueva;
    public string direccionVieja;
    public string direccionPrimeraVez;

    public bool primeraVezRotando;
    public bool rotando;
    public bool movimiento;
}
