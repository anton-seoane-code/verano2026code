using UnityEngine;

public class GameBootstrap : MonoBehaviour
{
    void Awake()
    {
        Cursor.lockState = CursorLockMode.Locked;

        SetupManagers();
        SetupPlayer();
        SetupEnvironment();
    }

    void SetupManagers()
    {
        if (GameManager.Instance == null)
        {
            var go = new GameObject("GameManager");
            go.AddComponent<GameManager>();
        }

        if (AudioManager.Instance == null)
        {
            var go = new GameObject("AudioManager");
            go.AddComponent<AudioManager>();
        }
    }

    void SetupPlayer()
    {
        var player = new GameObject("Player");
        player.transform.position = new Vector3(0f, 1.5f, -8f);

        var rb = player.AddComponent<Rigidbody>();
        rb.mass = 1f;
        rb.linearDamping = 0f;
        rb.angularDamping = 0.95f;

        var capsule = player.AddComponent<CapsuleCollider>();
        capsule.height = 1.8f;
        capsule.radius = 0.4f;
        capsule.center = new Vector3(0f, 0.9f, 0f);

        var camObj = new GameObject("PlayerCamera");
        camObj.transform.SetParent(player.transform);
        camObj.transform.localPosition = new Vector3(0f, 1.6f, 0f);
        var cam = camObj.AddComponent<Camera>();
        cam.nearClipPlane = 0.1f;
        cam.farClipPlane = 500f;
        camObj.AddComponent<AudioListener>();

        var playerController = player.AddComponent<PlayerController>();
        playerController.playerCamera = cam;

        var interactionSystem = player.AddComponent<InteractionSystem>();
        interactionSystem.playerCamera = cam;

        var hud = player.AddComponent<PlayerHUD>();
        hud.playerController = playerController;
    }

    void SetupEnvironment()
    {
        var env = new GameObject("EnvironmentManager");
        env.AddComponent<EnvironmentManager>();
    }
}
