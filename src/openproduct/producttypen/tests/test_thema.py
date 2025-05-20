from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from .factories import ThemaFactory


class TestThema(TestCase):
    def test_hoofd_thema_must_be_published_when_publishing_sub_thema(self):
        hoofd_thema = ThemaFactory.create(gepubliceerd=False)
        sub_thema = ThemaFactory.create(gepubliceerd=True, hoofd_thema=hoofd_thema)

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "Thema's moeten gepubliceerd zijn voordat sub-thema's kunnen worden gepubliceerd."
            ),
        ):
            sub_thema.clean()

        hoofd_thema.gepubliceerd = True
        hoofd_thema.save()

        sub_thema.clean()

    def test_hoofd_thema_cannot_be_unpublished_with_published_sub_themas(
        self,
    ):
        hoofd_thema = ThemaFactory.create(gepubliceerd=False)
        ThemaFactory.create(gepubliceerd=True, hoofd_thema=hoofd_thema)

        with self.assertRaisesMessage(
            ValidationError,
            _(
                "Thema's kunnen niet ongepubliceerd worden als ze gepubliceerde sub-thema's hebben."
            ),
        ):
            hoofd_thema.clean()

    def test_thema_cannot_reference_itself(self):
        thema = ThemaFactory.create()
        thema.hoofd_thema = thema

        with self.assertRaisesMessage(
            ValidationError, _("Een thema kan niet zijn eigen hoofd thema zijn.")
        ):
            thema.clean()
