#!/usr/bin/env python3
from opentelemetry import  trace
from opentelemetry.semconv.trace import HttpFlavorValues,SpanAttributes

from opentelemetry.propagate import inject

import requests
from common import configure_tracer

from opentelemetry.trace import Status, StatusCode

tracer = configure_tracer("shopper", "0.1.2")

@tracer.start_as_current_span("browse")
def browse():
    print("visiting the grocery store")
    with tracer.start_as_current_span(
        "web request", kind=trace.SpanKind.CLIENT,record_exception=False,set_status_on_exception=True,
    ) as span:
        headers = {}
        inject(headers)
        
        url = "http://localhost:5000/products"
        resp = requests.get(url, headers=headers)
        if resp:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(
            Status(StatusCode.ERROR, "status code: {}".
            format(resp.status_code))
        )
    add_item_to_cart("orange",5)

@tracer.start_as_current_span("add item to cart")
def add_item_to_cart(item,quantity):
    span = trace.get_current_span()
    span.set_attributes({
        "item": item,
        "quantity": quantity,
    })
    print("add {} to cart".format(item))

@tracer.start_as_current_span("visit store")
def visit_store():
    browse()

if __name__ == "__main__":
   visit_store()