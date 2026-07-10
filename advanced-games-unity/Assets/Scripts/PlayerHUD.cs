using UnityEngine;

public class PlayerHUD : MonoBehaviour
{
    [Header("References")]
    public PlayerController playerController;

    [Header("Crosshair")]
    public float crosshairSize = 10f;
    public float crosshairThickness = 2f;
    public Color crosshairColor = Color.white;

    [Header("Stamina Bar")]
    public float staminaBarWidth = 200f;
    public float staminaBarHeight = 8f;
    public float staminaBarOffsetX = 20f;
    public float staminaBarOffsetY = 40f;
    public Color staminaBarBackground = new Color(0f, 0f, 0f, 0.6f);
    public Color staminaBarFill = new Color(0.2f, 0.8f, 0.3f, 0.9f);
    public Color staminaBarDepleted = new Color(0.8f, 0.2f, 0.2f, 0.9f);

    [Header("Interaction Prompt")]
    public float promptFontSize = 18f;

    private Interactable currentInteractable;
    private GUIStyle promptStyle;
    private GUIStyle interactKeyStyle;
    private GUIStyle objectiveStyle;
    private GUIStyle discoveredStyle;
    private bool stylesInitialized;

    public void SetInteractable(Interactable interactable)
    {
        currentInteractable = interactable;
    }

    void OnGUI()
    {
        if (!stylesInitialized)
            InitStyles();

        DrawCrosshair();

        if (playerController != null)
            DrawStaminaBar();

        DrawInteractionPrompt();
        DrawDiscoveryCounter();
    }

    void InitStyles()
    {
        promptStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = (int)promptFontSize,
            alignment = TextAnchor.MiddleCenter,
            fontStyle = FontStyle.Bold
        };
        promptStyle.normal.textColor = Color.white;

        interactKeyStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = (int)(promptFontSize - 2),
            alignment = TextAnchor.MiddleCenter
        };
        interactKeyStyle.normal.textColor = Color.yellow;

        objectiveStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 14,
            alignment = TextAnchor.UpperLeft
        };
        objectiveStyle.normal.textColor = new Color(0.9f, 0.9f, 0.7f);

        discoveredStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 14,
            alignment = TextAnchor.UpperRight
        };
        discoveredStyle.normal.textColor = new Color(0.5f, 0.9f, 0.5f);

        stylesInitialized = true;
    }

    void DrawCrosshair()
    {
        float centerX = Screen.width * 0.5f;
        float centerY = Screen.height * 0.5f;

        Texture2D tex = Texture2D.whiteTexture;
        Color c = currentInteractable != null ? Color.yellow : crosshairColor;

        GUI.color = c;
        GUI.DrawTexture(new Rect(centerX - crosshairSize, centerY - crosshairThickness * 0.5f, crosshairSize * 2, crosshairThickness), tex);
        GUI.DrawTexture(new Rect(centerX - crosshairThickness * 0.5f, centerY - crosshairSize, crosshairThickness, crosshairSize * 2), tex);
        GUI.color = Color.white;
    }

    void DrawStaminaBar()
    {
        float x = staminaBarOffsetX;
        float y = Screen.height - staminaBarOffsetY;

        GUI.color = staminaBarBackground;
        GUI.DrawTexture(new Rect(x, y, staminaBarWidth, staminaBarHeight), Texture2D.whiteTexture);

        float ratio = playerController.CurrentStamina / playerController.MaxStamina;
        GUI.color = ratio > 0.2f ? staminaBarFill : staminaBarDepleted;
        GUI.DrawTexture(new Rect(x, y, staminaBarWidth * ratio, staminaBarHeight), Texture2D.whiteTexture);

        GUI.color = Color.white;
    }

    void DrawInteractionPrompt()
    {
        if (currentInteractable == null) return;

        float centerX = Screen.width * 0.5f;
        float promptY = Screen.height * 0.5f + 40f;

        GUI.color = Color.white;
        GUI.Label(new Rect(centerX - 100f, promptY, 200f, 30f), currentInteractable.interactionPrompt, promptStyle);
        GUI.color = Color.yellow;
        GUI.Label(new Rect(centerX - 100f, promptY + 25f, 200f, 25f), "[E]", interactKeyStyle);
        GUI.color = Color.white;
    }

    void DrawDiscoveryCounter()
    {
        if (GameManager.Instance == null) return;

        GUI.Label(new Rect(10f, 10f, 300f, 30f),
            $"Discoveries: {GameManager.Instance.Discoveries}/{GameManager.Instance.TotalDiscoveries}",
            discoveredStyle);
    }
}
