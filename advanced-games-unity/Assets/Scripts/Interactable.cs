using UnityEngine;

public class Interactable : MonoBehaviour
{
    public string interactionPrompt = "Interact";

    public System.Action OnInteracted;

    public virtual void Interact(GameObject interactor)
    {
        if (GameManager.Instance != null)
            GameManager.Instance.Discover();
        OnInteracted?.Invoke();
        OnInteract(interactor);
    }

    protected virtual void OnInteract(GameObject interactor) { }

    public virtual void OnFocusEnter() { }
    public virtual void OnFocusExit() { }
}
