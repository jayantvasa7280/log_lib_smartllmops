import os
from .sdk import SDKTracer
from .transport import Telemetry

def init(
    cosmos_conn=None,
    db_name=None,
    container_name=None,
    application_name=None,
    app_name=None,          # alias for application_name
    environment="prod",
    model=None,
    provider=None,
    tags=None,
    api_key=None,           # platform API key (stored as metadata, not used for Cosmos auth)
    framework=None,         # e.g. "LangChain", "CrewAI", "LlamaIndex"
):
    """Initializes and returns a tracer instance with optional auto-patching."""

    # app_name is a friendlier alias for application_name
    resolved_app_name = application_name or app_name

    # Auto-load from environment if not provided
    cosmos_conn     = cosmos_conn     or os.getenv("COSMOS_CONN_WRITE")
    db_name         = db_name         or os.getenv("COSMOS_DB")
    container_name  = container_name  or os.getenv("COSMOS_CONTAINER")

    if not cosmos_conn:
        print("⚠️ smartllmops: COSMOS_CONN_WRITE not found. Telemetry disabled.")
        return None

    telemetry = Telemetry(
        cosmos_conn=cosmos_conn,
        db_name=db_name,
        container_name=container_name
    )

    tracer = SDKTracer(
        telemetry,
        application_name=resolved_app_name,
        environment=environment,
        model=model,
        provider=provider,
        tags=tags,
        api_key=api_key,
        framework=framework,
    )

    # LangSmith-style: Auto-patch OpenAI if requested via env var
    if os.getenv("SMART_LLMOPS_AUTO_INSTRUMENT", "false").lower() == "true":
        tracer.patch_openai()

    return tracer

__all__ = ["SDKTracer", "Telemetry", "init"]
