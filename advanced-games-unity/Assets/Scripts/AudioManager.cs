using UnityEngine;

public class AudioManager : MonoBehaviour
{
    public static AudioManager Instance { get; private set; }

    [Header("Audio Sources")]
    public AudioSource ambientSource;
    public AudioSource sfxSource;

    [Header("Footstep Settings")]
    public AudioClip[] footstepClips;
    public float walkStepInterval = 0.5f;
    public float sprintStepInterval = 0.35f;
    public float footstepVolume = 0.4f;

    [Header("Ambient Settings")]
    public AudioClip ambientClip;
    public float ambientVolume = 0.15f;

    private PlayerController playerController;
    private float stepTimer;

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
    }

    void Start()
    {
        playerController = FindFirstObjectByType<PlayerController>();

        if (ambientSource == null)
        {
            ambientSource = gameObject.AddComponent<AudioSource>();
            ambientSource.loop = true;
            ambientSource.playOnAwake = false;
            ambientSource.volume = ambientVolume;
        }

        if (sfxSource == null)
        {
            sfxSource = gameObject.AddComponent<AudioSource>();
            sfxSource.playOnAwake = false;
        }

        if (ambientClip != null)
        {
            ambientSource.clip = ambientClip;
            ambientSource.Play();
        }
    }

    void Update()
    {
        if (playerController == null || footstepClips == null || footstepClips.Length == 0)
            return;

        if (!playerController.IsGrounded)
            return;

        Vector3 vel = GetComponent<Rigidbody>() != null
            ? GetComponent<Rigidbody>().linearVelocity
            : Vector3.zero;

        float horizontalSpeed = new Vector3(vel.x, 0f, vel.z).magnitude;
        if (horizontalSpeed < 0.5f)
        {
            stepTimer = 0f;
            return;
        }

        float interval = playerController.IsSprinting ? sprintStepInterval : walkStepInterval;
        stepTimer += Time.deltaTime;

        if (stepTimer >= interval)
        {
            stepTimer = 0f;
            PlayFootstep();
        }
    }

    void PlayFootstep()
    {
        if (footstepClips.Length == 0) return;
        AudioClip clip = footstepClips[Random.Range(0, footstepClips.Length)];
        float pitch = Random.Range(0.9f, 1.1f);
        sfxSource.pitch = pitch;
        sfxSource.PlayOneShot(clip, footstepVolume);
    }

    public void PlaySFX(AudioClip clip, float volume = 0.5f)
    {
        if (clip != null)
            sfxSource.PlayOneShot(clip, volume);
    }

    public void SetAmbientClip(AudioClip clip)
    {
        ambientSource.Stop();
        ambientClip = clip;
        if (clip != null)
        {
            ambientSource.clip = clip;
            ambientSource.Play();
        }
    }
}
