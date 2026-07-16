# ARM-Guard Architecture

```mermaid
flowchart LR
    A[Simulated frame / future camera input] --> B[EAR extraction]
    B --> C[Adaptive baseline profiler]
    C --> D[Drowsiness scorer]
    D --> E[Context-aware alert policy]
    E --> F[Alert escalation]
    D --> G[Anonymized event logger]
    A --> H[Device telemetry]
    H --> I[System reliability monitor]
    I --> F
```

Current implementation note: camera input is still simulated. The architecture is already separated so a live Arm64 landmark backend can replace the simulated provider without rewriting the privacy, scoring, alerting, or logging layers.
