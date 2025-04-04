from openproduct.utils.kanaal import Kanaal

from .models import Product

KANAAL_PRODUCTEN = Kanaal(
    "producten",
    main_resource=Product,
    kenmerken=(
        "producttype.id",
        "producttype.uniforme_product_naam",
        "producttype.code",
    ),
    extra_kwargs={"producttype.id": {"help_text": "uuid van het producttype"}},
)
