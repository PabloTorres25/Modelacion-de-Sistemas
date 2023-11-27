using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class Agente
{
    public int ID;
    public int[] Origen;
    public string Direccion;
    public string AltoSiguiente;

    public static Agente CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<Agente>(jsonString);
    }
   
}
