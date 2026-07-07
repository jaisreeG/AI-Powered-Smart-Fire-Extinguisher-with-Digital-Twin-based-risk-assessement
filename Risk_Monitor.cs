using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class FireRiskMonitor : MonoBehaviour
{
    public Material greenMaterial;
    public Material redMaterial;
    public GameObject statusBox;
    public ParticleSystem fireParticles;
    public ParticleSystem extinguisherParticles;

    private int lastRisk = -1;

    void Start()
    {
        StartCoroutine(CheckRisk());
    }

    IEnumerator CheckRisk()
    {
        while (true)
        {
            UnityWebRequest www = UnityWebRequest.Get("--link--");
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                string json = www.downloadHandler.text;
                int risk = JsonUtility.FromJson<RiskData>(json).risk;

                if (risk != lastRisk)
                {
                    UpdateVisuals(risk);
                    lastRisk = risk;
                }
            }

            yield return new WaitForSeconds(1);
        }
    }

    void UpdateVisuals(int risk)
    {
        if (risk == 1)
        {
            statusBox.GetComponent<Renderer>().material = redMaterial;
            fireParticles.Play();
            extinguisherParticles.Play();
        }
        else
        {
            statusBox.GetComponent<Renderer>().material = greenMaterial;
            fireParticles.Stop();
            extinguisherParticles.Stop();
        }
    }

    [System.Serializable]
    public class RiskData
    {
        public int risk;
    }
}
