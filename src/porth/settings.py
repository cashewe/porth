from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PorthSettings(BaseSettings):
    """Environment-backed configuration for Porth and its telemetry exporters."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    service_name: str = Field(
        default="porth",
        validation_alias="SERVICE_NAME",
        description="Name used to identify this service in telemetry resources.",
    )
    service_version: str = Field(
        default="0.1.0",
        validation_alias="SERVICE_VERSION",
        description="Deployed application version reported in telemetry resources.",
    )
    environment: str = Field(
        default="local",
        validation_alias="ENVIRONMENT",
        description="Deployment environment name, such as local, staging, or production.",
    )
    otel_service_instance_id: str = Field(
        default="local-instance",
        validation_alias="OTEL_SERVICE_INSTANCE_ID",
        description="Unique identifier for this running instance of the service.",
    )
    otel_resource_attributes: str | None = Field(
        default=None,
        validation_alias="OTEL_RESOURCE_ATTRIBUTES",
        description="Comma-separated OpenTelemetry resource attributes added to telemetry.",
    )
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT",
        description="Shared OTLP collector endpoint used when no signal endpoint overrides it.",
    )
    otel_exporter_otlp_traces_endpoint: str | None = Field(
        default=None,
        validation_alias="OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        description="OTLP collector endpoint used specifically for trace export.",
    )
    otel_exporter_otlp_metrics_endpoint: str | None = Field(
        default=None,
        validation_alias="OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        description="OTLP collector endpoint that enables and receives metric export.",
    )
    otel_exporter_otlp_headers: str | None = Field(
        default=None,
        validation_alias="OTEL_EXPORTER_OTLP_HEADERS",
        description="Comma-separated authentication or metadata headers for OTLP export.",
    )
    otel_exporter_otlp_traces_headers: str | None = Field(
        default=None,
        validation_alias="OTEL_EXPORTER_OTLP_TRACES_HEADERS",
        description="Trace-specific OTLP headers that override the shared exporter headers.",
    )
    otel_exporter_otlp_metrics_headers: str | None = Field(
        default=None,
        validation_alias="OTEL_EXPORTER_OTLP_METRICS_HEADERS",
        description="Metric-specific OTLP headers that override the shared exporter headers.",
    )
    otel_traces_sampler: str = Field(
        default="parentbased_always_on",
        validation_alias="OTEL_TRACES_SAMPLER",
        description="OpenTelemetry sampler used to decide which traces are recorded.",
    )
    otel_traces_sampler_arg: str | None = Field(
        default=None,
        validation_alias="OTEL_TRACES_SAMPLER_ARG",
        description="Optional argument supplied to the configured OpenTelemetry sampler.",
    )


settings = PorthSettings()
