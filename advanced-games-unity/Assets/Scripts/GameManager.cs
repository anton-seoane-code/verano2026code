using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    private int discoveries;
    private int totalDiscoveries;

    public int Discoveries => discoveries;
    public int TotalDiscoveries => totalDiscoveries;

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    public void RegisterDiscoverable()
    {
        totalDiscoveries++;
    }

    public void Discover()
    {
        discoveries++;
        if (discoveries >= totalDiscoveries)
            Debug.Log("[GameManager] All discoveries found!");
    }
}
