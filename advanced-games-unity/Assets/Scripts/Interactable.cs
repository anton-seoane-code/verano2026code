using UnityEngine;

public class Interactable : MonoBehaviour
{
    public string interactionPrompt = "Interact";
    public bool requireLineOfSight = true;
    public bool isHighlighted = true;

    public System.Action OnInteracted;

    public virtual void Interact(GameObject interactor)
    {
        OnInteracted?.Invoke();
        OnInteract(interactor);
    }

    protected virtual void OnInteract(GameObject interactor) { }

    public virtual void OnFocusEnter() { }
    public virtual void OnFocusExit() { }
}
