from openproduct.utils.kanaal import Kanaal

from .models import Product

KANAAL_PRODUCTEN = Kanaal(
    "producten",
    main_resource=Product,
    kenmerken=(
        "producttype.uuid",
        "producttype.uniforme_product_naam",
        "producttype.code",
    ),
    extra_kwargs={"producttype.uuid": {"help_text": "uuid van het producttype"}},
)
