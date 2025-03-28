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
)
