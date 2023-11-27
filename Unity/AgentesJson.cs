using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AgentesJson
{
    public List<Agente> autos;

    public static AgentesJson CreateFromJSON(string agentesJSON)
    {
        return JsonUtility.FromJson<AgentesJson>(agentesJSON);
    }
}
