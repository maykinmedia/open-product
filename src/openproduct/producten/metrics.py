from opentelemetry import metrics

meter = metrics.get_meter("openproduct.producten")

product_create_counter = meter.create_counter(
    "openproduct.producten.creates",
    description="Amount of producten created (via the API).",
    unit="1",
)
product_update_counter = meter.create_counter(
    "openproduct.producten.updates",
    description="Amount of producten updated (via the API).",
    unit="1",
)
product_delete_counter = meter.create_counter(
    "openproduct.producten.deletes",
    description="Amount of producten deleted (via the API).",
    unit="1",
)
