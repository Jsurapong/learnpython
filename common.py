#!/usr/bin/env python3
from opentelemetry import  trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter,BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

from local_machine_resource_detector import LocalMachineResourceDetector

from flask import request
from opentelemetry.semconv.trace import SpanAttributes

def set_span_attributes_from_flask():
    span = trace.get_current_span()
    span.set_attributes(
        {
            SpanAttributes.HTTP_FLAVOR: request.environ.get("SERVER_PROTOCOL"),
            SpanAttributes.HTTP_METHOD: request.method,
            SpanAttributes.HTTP_USER_AGENT: str(request.user_agent),
            SpanAttributes.HTTP_HOST: request.host,
            SpanAttributes.HTTP_SCHEME: request.scheme,
            SpanAttributes.HTTP_TARGET: request.path,
            SpanAttributes.HTTP_CLIENT_IP: request.remote_addr,
        }
    )

def configure_tracer(name, version):
    exporter = ConsoleSpanExporter()
    span_processor = BatchSpanProcessor(exporter)
    
    local_resource = LocalMachineResourceDetector().detect()
    resource = local_resource.merge(
        Resource.create(
            {
                "service.name": name,
                "service.version": version,
            }
        )
    )
    provider = TracerProvider(resource=resource)

    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)

    return trace.get_tracer(name, version)