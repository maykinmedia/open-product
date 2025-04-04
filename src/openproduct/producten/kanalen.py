from openproduct.utils.kanaal import Kanaal

from .models import Product

KANAAL_PRODUCTEN = Kanaal(
    "producten",
    main_resource=Product,
    kenmerken=(
        "product_type.id",
        "product_type.uniforme_product_naam",
        "product_type.code",
    ),
)
