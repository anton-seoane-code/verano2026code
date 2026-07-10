using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    public float speed = 8f;
    public float sprintSpeed = 14f;
    public float crouchSpeed = 3f;
    public float jumpForce = 5f;
    public float airControlMultiplier = 0.4f;

    [Header("Sprint Settings")]
    public float maxStamina = 100f;
    public float staminaDrainRate = 20f;
    public float staminaRegenRate = 15f;
    public float minStaminaToSprint = 10f;

    [Header("Crouch Settings")]
    public float crouchHeight = 0.8f;
    public float standHeight = 1.8f;
    public float crouchTransitionSpeed = 8f;

    [Header("Camera Settings")]
    public Camera playerCamera;
    public float mouseSensitivity = 2f;
    public float maxLookAngle = 80f;

    [Header("Ground Check")]
    public float groundCheckDistance = 0.15f;
    public LayerMask groundMask = -1;

    private Rigidbody rb;
    private float xRotation = 0f;
    private bool isGrounded;
    private Vector3 moveInput;

    private bool isSprinting;
    private float currentStamina;
    private bool isCrouching;
    private float currentHeight;
    private CapsuleCollider capsule;

    public bool IsSprinting => isSprinting;
    public bool IsCrouching => isCrouching;
    public float CurrentStamina => currentStamina;
    public float MaxStamina => maxStamina;
    public bool IsGrounded => isGrounded;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        rb.freezeRotation = true;
        capsule = GetComponent<CapsuleCollider>();
        currentStamina = maxStamina;
        currentHeight = standHeight;

        if (playerCamera == null)
            playerCamera = Camera.main;

        Cursor.lockState = CursorLockMode.Locked;
    }

    void Update()
    {
        HandleMouseLook();
        HandleJumpInput();
        HandleSprintInput();
        HandleCrouchInput();
        UpdateStamina();
        UpdateCrouchHeight();
    }

    void FixedUpdate()
    {
        CheckGround();
        HandleMovement();
    }

    void HandleMouseLook()
    {
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

        xRotation -= mouseY;
        xRotation = Mathf.Clamp(xRotation, -maxLookAngle, maxLookAngle);

        playerCamera.transform.localRotation = Quaternion.Euler(xRotation, 0f, 0f);
        transform.Rotate(Vector3.up * mouseX);
    }

    void HandleJumpInput()
    {
        if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
        {
            if (isCrouching)
                ToggleCrouch();
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
    }

    void HandleSprintInput()
    {
        bool wantsToSprint = Input.GetKey(KeyCode.LeftShift) && !isCrouching;
        isSprinting = wantsToSprint && currentStamina > minStaminaToSprint && isGrounded;
    }

    void HandleCrouchInput()
    {
        if (Input.GetKeyDown(KeyCode.LeftControl))
            ToggleCrouch();
    }

    void ToggleCrouch()
    {
        isCrouching = !isCrouching;
        if (isCrouching)
            isSprinting = false;
    }

    void UpdateStamina()
    {
        if (isSprinting)
            currentStamina -= staminaDrainRate * Time.deltaTime;
        else
            currentStamina += staminaRegenRate * Time.deltaTime;

        currentStamina = Mathf.Clamp(currentStamina, 0f, maxStamina);
    }

    void UpdateCrouchHeight()
    {
        float targetHeight = isCrouching ? crouchHeight : standHeight;
        currentHeight = Mathf.Lerp(currentHeight, targetHeight, crouchTransitionSpeed * Time.deltaTime);
        capsule.height = currentHeight;
        capsule.center = new Vector3(0f, currentHeight * 0.5f, 0f);
    }

    void HandleMovement()
    {
        float horizontal = Input.GetAxisRaw("Horizontal");
        float vertical = Input.GetAxisRaw("Vertical");

        Vector3 forward = transform.forward;
        Vector3 right = transform.right;
        forward.y = 0f;
        right.y = 0f;
        forward.Normalize();
        right.Normalize();

        float currentSpeed = isCrouching ? crouchSpeed : (isSprinting ? sprintSpeed : speed);
        Vector3 targetVelocity = (forward * vertical + right * horizontal).normalized * currentSpeed;
        targetVelocity.y = rb.linearVelocity.y;

        if (!isGrounded)
            targetVelocity *= airControlMultiplier;

        Vector3 velocityChange = targetVelocity - rb.linearVelocity;
        velocityChange.y = 0f;

        rb.AddForce(velocityChange, ForceMode.VelocityChange);
    }

    void CheckGround()
    {
        isGrounded = Physics.CheckSphere(
            transform.position - Vector3.up * groundCheckDistance,
            0.1f,
            groundMask
        );
    }

    void OnDrawGizmosSelected()
    {
        Gizmos.color = isGrounded ? Color.green : Color.red;
        Gizmos.DrawWireSphere(
            transform.position - Vector3.up * groundCheckDistance,
            0.1f
        );
    }
}
