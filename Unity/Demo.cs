using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections.Generic;
using UnityEngine.ProBuilder.Shapes;
using System.Linq;

public class Demo : MonoBehaviour
{

    // Variables a utilizar
    private float tiempoTranscurrido;
    public float intervalo; // Intervalo de tiempo en segundos
    private string jsonString; // Variable para almacenar el JSON obtenido


    Dictionary<int, DatosPersonalizados> diccionarioAgentes;    // Diccionario para alojar los agentes y sus datos


    // Start is called before the first frame update
    void Start()
    {
        tiempoTranscurrido = 0f;
        intervalo = 1f;
        diccionarioAgentes = new Dictionary<int, DatosPersonalizados>();
    }

    // Update is called once per frame
    void Update()
    {
        tiempoTranscurrido += Time.deltaTime; // Incrementa el tiempo transcurrido con el tiempo de cada fotograma

        if (tiempoTranscurrido >= intervalo)
        {
            // Realiza la acción que deseas ejecutar cada segundo aquí
            AccionCadaSegundo();

            tiempoTranscurrido = 0f; // Reinicia el contador de tiempo
        }

        foreach (KeyValuePair<int, DatosPersonalizados> kvp in diccionarioAgentes)
        {
            if(kvp.Value.movimiento)
            {
                kvp.Value.z += 0.00001f; 
            }
            else
            {
                kvp.Value.z = 0;
            }

            if (kvp.Value.rotando)
            {
                // Lógica de rotar
            }
            else
            {
                kvp.Value.aTrans = VecOps.TranslateM(0, 0, kvp.Value.z);
                kvp.Value.aRot = VecOps.RotateY(kvp.Value.y);
                kvp.Value.matrix = kvp.Value.currMat * kvp.Value.aTrans * kvp.Value.aRot * kvp.Value.aEscala;
                kvp.Value.agenteAuto.GetComponent<MeshFilter>().mesh.vertices = VecOps.ApplyTransform(kvp.Value.autoOriginals, kvp.Value.matrix).ToArray();
                kvp.Value.currMat = kvp.Value.currMat * kvp.Value.aTrans * kvp.Value.aRot;
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
        datosAgente.agenteAuto = GameObject.CreatePrimitive(PrimitiveType.Cube);
        datosAgente.autoOriginals = datosAgente.agenteAuto.GetComponent<MeshFilter>().mesh.vertices.ToList();
        
        datosAgente.aEscala = VecOps.ScaleM(1f, 1f, 1f);
        datosAgente.currMat = VecOps.TranslateM(xC, 5, zC);
        datosAgente.aTrans = Matrix4x4.identity;
        datosAgente.aRot = Matrix4x4.identity;

        datosAgente.y = 0;
        datosAgente.z = 0;
        datosAgente.contadorY = 0;

        datosAgente.movimiento = true;
        datosAgente.rotando = false;
        /*
        // Establecer la rotación del agente basada en la dirección
        if (direccion == "Ar") 
        {
            datosAgente.agenteAuto.transform.rotation = Quaternion.Euler(0f, 0f, 0f); 
        }
        else if (direccion == "Ab")
        {
            datosAgente.agenteAuto.transform.rotation = Quaternion.Euler(0f, 180f, 0f); 
        }
        else if (direccion == "De")
        {
            datosAgente.agenteAuto.transform.rotation = Quaternion.Euler(0f, 90f, 0f); 
        }
        else if (direccion == "Iz")
        {
            datosAgente.agenteAuto.transform.rotation = Quaternion.Euler(0f, -90f, 0f); 
        }*/

        diccionarioAgentes.Add(id, datosAgente);
        Debug.Log(direccion);
        Debug.Log("X:   "+ xC);
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
                    CrearAgente(data.ID, data.Origen[0], data.Origen[1], data.Direccion);
                }
                else if (data.AltoSiguiente == "Destino")
                {
                    GameObject objetoAsociado = diccionarioAgentes[data.ID].agenteAuto;
                    GameObject.Destroy(objetoAsociado);
                    diccionarioAgentes.Remove(data.ID);
                }
                else if (data.AltoSiguiente == "Vehiculo enfrente" || data.AltoSiguiente == "En semaforo(rojo)")
                {
                    DatosPersonalizados datosAgente = diccionarioAgentes[data.ID];
                    datosAgente.movimiento = false;
                    datosAgente.direccionVieja = data.Direccion;
                    diccionarioAgentes[data.ID] = datosAgente;
                }
                else if (data.AltoSiguiente == "Girando")
                {
                    DatosPersonalizados datosAgente = diccionarioAgentes[data.ID];
                    datosAgente.movimiento = false;
                    datosAgente.direccionNueva = data.Direccion;
                    datosAgente.rotando = true;
                    diccionarioAgentes[data.ID] = datosAgente;

                }
                else if (data.AltoSiguiente == null)
                {
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

    public float currX;
    public float currZ;
    public float z;
    public float y;
    public float contadorY;

    public string direccionNueva;
    public string direccionVieja;

    public bool rotando;
    public bool movimiento;
}