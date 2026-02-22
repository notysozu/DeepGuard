# API Reference

## Authentication

### POST `/auth/token`
OAuth2 password flow endpoint.

Request: `application/x-www-form-urlencoded`
- `username`
- `password`

Response:
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

## Detection

### POST `/predict`
Authenticated multipart upload endpoint.

- Validates MIME and payload limits
- Generates SHA-256 hash
- Reuses cached verdict for duplicate media
- Calls model services in parallel with retries/timeouts
- Applies ensemble fusion
- Stores full audit record

User response does **not** expose raw probabilities.

Response shape:
```json
{
  "request_id": "uuid",
  "media_type": "image",
  "verdict": "fake",
  "confidence": 0.91,
  "ensemble_method": "stacking",
  "model_count": 2,
  "inference_time": 0.24,
  "duplicate_cache_hit": false
}
```

### POST `/detect`
Alias to `/predict` for web UI integration.

## History

### GET `/history`
Returns detection list (audit metadata).

### GET `/history/{request_id}`
Returns full stored detection JSON.

## Health

### GET `/health`
Returns gateway status.
