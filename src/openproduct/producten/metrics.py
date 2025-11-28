from opentelemetry import metrics

meter = metrics.get_meter("openproduct.product")

product_create_counter = meter.create_counter(
    "openproduct.product.creates",
    description="Amount of producten created (via the API).",
    unit="1",
)
product_update_counter = meter.create_counter(
    "openproduct.product.updates",
    description="Amount of producten updated (via the API).",
    unit="1",
)
product_delete_counter = meter.create_counter(
    "openproduct.product.deletes",
    description="Amount of producten deleted (via the API).",
    unit="1",
)
