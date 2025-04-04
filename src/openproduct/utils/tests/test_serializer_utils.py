from django.test import TestCase

from ..serializers import clean_duplicate_ids_in_list


class TestDuplicateIds(TestCase):

    def test_list_has_duplicates(self):
        errors = dict()
        values = ["123", "123"]

        clean_duplicate_ids_in_list(values, "test", errors)

        self.assertEqual(errors, {"test": ["Dubbel id: 123 op index 1."]})

    def test_list_has_multiple_duplicates(self):
        errors = dict()
        values = ["123", "123", "456", "456"]

        clean_duplicate_ids_in_list(values, "test", errors)

        self.assertEqual(
            errors,
            {"test": ["Dubbel id: 123 op index 1.", "Dubbel id: 456 op index 3."]},
        )

    def test_list_has_no_duplicates(self):
        errors = dict()
        values = ["123", "456"]
        clean_duplicate_ids_in_list(values, "test", errors)
        self.assertEqual(errors, {})
