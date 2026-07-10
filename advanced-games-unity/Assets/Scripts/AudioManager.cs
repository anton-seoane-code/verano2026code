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
    private Rigidbody playerRb;
    private float stepTimer;

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

    void Start()
    {
        playerController = FindFirstObjectByType<PlayerController>();
        if (playerController != null)
            playerRb = playerController.GetComponent<Rigidbody>();

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

        if (footstepClips == null || footstepClips.Length == 0)
            GenerateFootstepClips();

        if (ambientClip == null)
            GenerateAmbientClip();

        ambientSource.clip = ambientClip;
        ambientSource.Play();
    }

    void Update()
    {
        if (playerController == null || playerRb == null || footstepClips == null || footstepClips.Length == 0)
            return;

        if (!playerController.IsGrounded)
            return;

        Vector3 vel = playerRb.linearVelocity;
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

    void GenerateFootstepClips()
    {
        int sampleRate = 44100;
        float duration = 0.12f;
        int samples = Mathf.FloorToInt(sampleRate * duration);
        footstepClips = new AudioClip[3];
        for (int i = 0; i < 3; i++)
        {
            float[] data = new float[samples];
            for (int j = 0; j < samples; j++)
            {
                float t = (float)j / sampleRate;
                data[j] = Mathf.Sin(2f * Mathf.PI * 200f * t) * Mathf.Exp(-t * 35f);
                data[j] += (Random.value - 0.5f) * 0.4f * Mathf.Exp(-t * 25f);
            }
            var clip = AudioClip.Create($"Footstep_{i}", samples, 1, sampleRate, false);
            clip.SetData(data, 0);
            footstepClips[i] = clip;
        }
    }

    void GenerateAmbientClip()
    {
        int sampleRate = 44100;
        float duration = 5f;
        int samples = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[samples];
        for (int i = 0; i < samples; i++)
        {
            float t = (float)i / sampleRate;
            data[i] = Mathf.Sin(2f * Mathf.PI * 55f * t) * 0.15f;
            data[i] += Mathf.Sin(2f * Mathf.PI * 85f * t) * 0.08f;
        }
        ambientClip = AudioClip.Create("AmbientWind", samples, 1, sampleRate, false);
        ambientClip.SetData(data, 0);
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
