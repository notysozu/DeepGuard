from api_gateway.app.core.config import settings



def resolve_model_endpoints(media_type: str) -> list[str]:
    # V1: generic model endpoints, optionally provided by MODEL_URLS env var.
    # media_type is reserved for type-specific routing in V2.
    _ = media_type
    return settings.model_urls
