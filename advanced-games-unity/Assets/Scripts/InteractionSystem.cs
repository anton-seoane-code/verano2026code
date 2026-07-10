using UnityEngine;

public class InteractionSystem : MonoBehaviour
{
    [Header("Raycast Settings")]
    public float interactionRange = 5f;
    public LayerMask interactionMask = ~0;

    [Header("References")]
    public Camera playerCamera;

    private Interactable currentTarget;
    private PlayerHUD hud;

    public Interactable CurrentTarget => currentTarget;

    void Start()
    {
        if (playerCamera == null)
            playerCamera = Camera.main;
        hud = GetComponent<PlayerHUD>();
    }

    void Update()
    {
        UpdateTarget();

        if (Input.GetKeyDown(KeyCode.E) && currentTarget != null)
            currentTarget.Interact(gameObject);
    }

    void UpdateTarget()
    {
        Interactable newTarget = null;

        if (playerCamera != null)
        {
            Ray ray = new Ray(playerCamera.transform.position, playerCamera.transform.forward);
            if (Physics.Raycast(ray, out RaycastHit hit, interactionRange, interactionMask))
            {
                newTarget = hit.collider.GetComponentInParent<Interactable>();
            }
        }

        if (newTarget != currentTarget)
        {
            if (currentTarget != null)
                currentTarget.OnFocusExit();

            currentTarget = newTarget;

            if (currentTarget != null)
                currentTarget.OnFocusEnter();
        }

        if (hud != null)
            hud.SetInteractable(currentTarget);
    }

    void OnDrawGizmosSelected()
    {
        if (playerCamera == null) return;
        Gizmos.color = currentTarget != null ? Color.yellow : Color.gray;
        Gizmos.DrawLine(playerCamera.transform.position,
            playerCamera.transform.position + playerCamera.transform.forward * interactionRange);
    }
}
