# System Workflow Validation

1. User uploads media through UI or API.
2. API Gateway assigns UUID.
3. Media is validated (MIME, payload size, image dimension guard).
4. SHA-256 hash is generated.
5. Hash is checked in database.
6. If duplicate: cached verdict is returned.
7. If new: media is base64-encoded.
8. Gateway queries configured model services in parallel with retry/timeout.
9. Ensemble engine fuses outputs using configured method (stacking default).
10. Binary verdict is generated using threshold logic.
11. Response is logged with forensic metadata.
12. UI displays only red/green verdict with confidence, model count, and latency.
