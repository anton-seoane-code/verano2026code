using UnityEngine;

public class EnvironmentManager : MonoBehaviour
{
    [Header("World Size")]
    public float groundSize = 120f;
    public int pillarCount = 18;
    public int wallSegmentCount = 8;
    public int treeCount = 25;
    public int ruinPileCount = 12;

    private Material groundMat;
    private Material stoneMat;
    private Material darkStoneMat;
    private Material treeTrunkMat;
    private Material foliageMat;
    private Material pathMat;
    private GameObject environmentParent;

    void Awake()
    {
        CreateMaterials();
        BuildEnvironment();
    }

    void CreateMaterials()
    {
        groundMat = CreateMat(new Color(0.35f, 0.45f, 0.25f));
        stoneMat = CreateMat(new Color(0.6f, 0.58f, 0.52f));
        darkStoneMat = CreateMat(new Color(0.45f, 0.42f, 0.38f));
        treeTrunkMat = CreateMat(new Color(0.35f, 0.25f, 0.15f));
        foliageMat = CreateMat(new Color(0.2f, 0.4f, 0.15f));
        pathMat = CreateMat(new Color(0.5f, 0.45f, 0.35f));
    }

    Material CreateMat(Color color)
    {
        var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        mat.SetColor("_BaseColor", color);
        return mat;
    }

    void BuildEnvironment()
    {
        environmentParent = new GameObject("Environment");

        BuildLighting();
        BuildGround();
        BuildStonePath();
        BuildPillars();
        BuildWalls();
        BuildTrees();
        BuildRuinPiles();
        BuildCentralAltar();
    }

    void BuildLighting()
    {
        RenderSettings.fog = true;
        RenderSettings.fogMode = FogMode.ExponentialSquared;
        RenderSettings.fogColor = new Color(0.75f, 0.8f, 0.7f);
        RenderSettings.fogDensity = 0.008f;
        RenderSettings.ambientLight = new Color(0.45f, 0.5f, 0.4f);
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;

        var sun = new GameObject("Directional Light");
        sun.transform.SetParent(environmentParent.transform);
        var light = sun.AddComponent<Light>();
        light.type = LightType.Directional;
        light.color = new Color(1f, 0.95f, 0.8f);
        light.intensity = 1.2f;
        light.shadows = LightShadows.Soft;
        light.shadowStrength = 0.8f;
        sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
    }

    void BuildGround()
    {
        var ground = CreateBlock("Ground", groundSize, 0.5f, groundSize, Vector3.down * 0.25f);
        ground.GetComponent<Renderer>().material = groundMat;
        ground.isStatic = true;
    }

    void BuildStonePath()
    {
        for (int i = -20; i <= 20; i += 2)
        {
            float width = 2.5f - Mathf.Abs(i) * 0.02f;
            var stone = CreateBlock($"PathStone_{i}", width, 0.15f, 1.8f,
                new Vector3(i * 0.3f, 0.05f, 0f));
            stone.GetComponent<Renderer>().material = pathMat;
            stone.transform.rotation = Quaternion.Euler(0f, Random.Range(-5f, 5f), 0f);
            stone.isStatic = true;
        }

        for (int i = -15; i <= 15; i += 3)
        {
            var stone = CreateBlock($"PathCross_{i}", 1.8f, 0.15f, 2f,
                new Vector3(0f, 0.05f, i * 2f));
            stone.GetComponent<Renderer>().material = pathMat;
            stone.isStatic = true;
        }
    }

    void BuildPillars()
    {
        for (int i = 0; i < pillarCount; i++)
        {
            float angle = (360f / pillarCount) * i + Random.Range(-8f, 8f);
            float radius = Random.Range(15f, 35f);
            float x = Mathf.Cos(angle * Mathf.Deg2Rad) * radius;
            float z = Mathf.Sin(angle * Mathf.Deg2Rad) * radius;

            float height = Random.Range(2f, 6f);
            float width = Random.Range(0.6f, 1.2f);

            var pillar = CreateBlock($"Pillar_{i}", width, height, width,
                new Vector3(x, height * 0.5f, z));
            pillar.GetComponent<Renderer>().material = i % 3 == 0 ? darkStoneMat : stoneMat;
            pillar.isStatic = true;

            if (height > 3.5f && Random.value > 0.5f)
            {
                float topWidth = width * Random.Range(1.2f, 1.6f);
                var cap = CreateBlock($"PillarCap_{i}", topWidth, 0.4f, topWidth,
                    new Vector3(x, height + 0.2f, z));
                cap.GetComponent<Renderer>().material = stoneMat;
                cap.isStatic = true;
            }

            if (Random.value > 0.6f)
            {
                float brokenHeight = height * Random.Range(0.3f, 0.6f);
                var broken = CreateBlock($"BrokenPillar_{i}", width * 0.7f, brokenHeight, width * 0.7f,
                    new Vector3(x + Random.Range(-2f, 2f), brokenHeight * 0.5f, z + Random.Range(-2f, 2f)));
                broken.GetComponent<Renderer>().material = darkStoneMat;
                broken.transform.rotation = Quaternion.Euler(Random.Range(-15f, 15f), Random.Range(0f, 360f), Random.Range(-15f, 15f));
                broken.isStatic = true;
            }
        }
    }

    void BuildWalls()
    {
        for (int i = 0; i < wallSegmentCount; i++)
        {
            float angle = (360f / wallSegmentCount) * i + Random.Range(-10f, 10f);
            float radius = Random.Range(25f, 40f);
            float x = Mathf.Cos(angle * Mathf.Deg2Rad) * radius;
            float z = Mathf.Sin(angle * Mathf.Deg2Rad) * radius;

            float wallLength = Random.Range(4f, 10f);
            float wallHeight = Random.Range(1.5f, 3.5f);
            float wallThickness = Random.Range(0.4f, 0.8f);

            var wall = CreateBlock($"Wall_{i}", wallLength, wallHeight, wallThickness,
                new Vector3(x, wallHeight * 0.5f, z));
            wall.GetComponent<Renderer>().material = i % 2 == 0 ? stoneMat : darkStoneMat;
            wall.transform.rotation = Quaternion.Euler(0f, angle + 90f, 0f);
            wall.isStatic = true;
        }
    }

    void BuildTrees()
    {
        for (int i = 0; i < treeCount; i++)
        {
            float x = Random.Range(-groundSize * 0.4f, groundSize * 0.4f);
            float z = Random.Range(-groundSize * 0.4f, groundSize * 0.4f);

            if (Mathf.Abs(x) < 5f && Mathf.Abs(z) < 5f)
                continue;

            float trunkHeight = Random.Range(2.5f, 5f);
            float trunkWidth = Random.Range(0.25f, 0.5f);

            var trunk = CreateBlock($"Trunk_{i}", trunkWidth, trunkHeight, trunkWidth,
                new Vector3(x, trunkHeight * 0.5f, z));
            trunk.GetComponent<Renderer>().material = treeTrunkMat;
            trunk.isStatic = true;

            float canopyRadius = Random.Range(1.5f, 3f);
            var canopy = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            canopy.name = $"Canopy_{i}";
            canopy.transform.SetParent(environmentParent.transform);
            canopy.transform.position = new Vector3(x, trunkHeight + canopyRadius * 0.5f, z);
            canopy.transform.localScale = new Vector3(canopyRadius * 2f, canopyRadius * 1.6f, canopyRadius * 2f);
            canopy.GetComponent<Renderer>().material = foliageMat;
            canopy.isStatic = true;
            Destroy(canopy.GetComponent<SphereCollider>());
        }
    }

    void BuildRuinPiles()
    {
        for (int i = 0; i < ruinPileCount; i++)
        {
            float x = Random.Range(-30f, 30f);
            float z = Random.Range(-30f, 30f);

            if (Mathf.Abs(x) < 4f && Mathf.Abs(z) < 4f)
                continue;

            int rockCount = Random.Range(3, 7);
            for (int j = 0; j < rockCount; j++)
            {
                float rx = x + Random.Range(-1.5f, 1.5f);
                float rz = z + Random.Range(-1.5f, 1.5f);
                float size = Random.Range(0.4f, 1.2f);

                var rock = CreateBlock($"RuinRock_{i}_{j}", size, size * 0.6f, size * 0.8f,
                    new Vector3(rx, size * 0.3f, rz));
                rock.GetComponent<Renderer>().material = Random.value > 0.5f ? stoneMat : darkStoneMat;
                rock.transform.rotation = Quaternion.Euler(Random.Range(-20f, 20f), Random.Range(0f, 360f), Random.Range(-20f, 20f));
                rock.isStatic = true;
            }
        }
    }

    void BuildCentralAltar()
    {
        var altarBase = CreateBlock("AltarBase", 4f, 0.8f, 4f, new Vector3(0f, 0.4f, 0f));
        altarBase.GetComponent<Renderer>().material = darkStoneMat;
        altarBase.isStatic = true;

        var altarTop = CreateBlock("AltarTop", 2.5f, 0.3f, 2.5f, new Vector3(0f, 1.1f, 0f));
        altarTop.GetComponent<Renderer>().material = stoneMat;
        altarTop.isStatic = true;

        for (int i = 0; i < 4; i++)
        {
            float angle = 90f * i;
            float x = Mathf.Cos(angle * Mathf.Deg2Rad) * 1.8f;
            float z = Mathf.Sin(angle * Mathf.Deg2Rad) * 1.8f;

            var post = CreateBlock($"AltarPost_{i}", 0.3f, 1.5f, 0.3f,
                new Vector3(x, 1.75f, z));
            post.GetComponent<Renderer>().material = stoneMat;
            post.isStatic = true;
        }

        var marker = new GameObject("DiscoveryMarker_Altar");
        marker.transform.SetParent(environmentParent.transform);
        marker.transform.position = new Vector3(0f, 2f, 0f);
        var interactable = marker.AddComponent<Interactable>();
        interactable.interactionPrompt = "Ancient Altar";
        if (GameManager.Instance != null)
            GameManager.Instance.RegisterDiscoverable();
    }

    GameObject CreateBlock(string name, float width, float height, float depth, Vector3 position)
    {
        var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        obj.name = name;
        obj.transform.SetParent(environmentParent.transform);
        obj.transform.position = position;
        obj.transform.localScale = new Vector3(width, height, depth);
        return obj;
    }
}
