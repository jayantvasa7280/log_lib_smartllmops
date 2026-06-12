import os
try:
    from dotenv import load_dotenv
    # Resolve the library's absolute root directory where its .env is located
    lib_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(lib_root, ".env")
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

from .sdk import SDKTracer
from .transport import Telemetry

def init(
    cosmos_conn=None,
    db_name=None,
    container_name=None,
    application_name=None,
    app_name=None,          # alias for application_name
    app_id=None,            # new parameter for Multi-Tenancy
    application_id=None,    # alias for app_id
    environment="prod",
    model=None,
    provider=None,
    tags=None,
    api_key=None,           # platform API key (stored as metadata, not used for Cosmos auth)
    framework=None,         # e.g. "LangChain", "CrewAI", "LlamaIndex"
):
    """Initializes and returns a tracer instance with optional auto-patching."""

    # Resolve app_id and application_name aliases
    resolved_app_name = application_name or app_name
    resolved_app_id = app_id or application_id

    # Auto-load from environment if not provided
    cosmos_conn     = cosmos_conn     or os.getenv("COSMOS_CONN_WRITE")
    db_name         = db_name         or os.getenv("COSMOS_DB")
    container_name  = container_name  or os.getenv("COSMOS_CONTAINER")

    if not cosmos_conn:
        print("⚠️ smartllmops: COSMOS_CONN_WRITE not found. Falling back to local offline logging.")

    telemetry = Telemetry(
        cosmos_conn=cosmos_conn,
        db_name=db_name,
        container_name=container_name
    )

    tracer = SDKTracer(
        telemetry,
        app_id=resolved_app_id,
        application_name=resolved_app_name,
        environment=environment,
        framework=framework,
        model=model,
        provider=provider,
        tags=tags,
        api_key=api_key,
    )

    # LangSmith-style: Auto-patch OpenAI if requested via env var
    if os.getenv("SMART_LLMOPS_AUTO_INSTRUMENT", "false").lower() == "true":
        tracer.patch_openai()

    return tracer

__all__ = ["SDKTracer", "Telemetry", "init"]
