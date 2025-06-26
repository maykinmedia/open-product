import csv
import io
import json
import zipfile
from itertools import chain

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.db.models import ForeignKey, ManyToManyRel, ManyToOneRel, OneToOneField
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = "Export productype(s)"

    def add_arguments(self, parser):
        parser.add_argument(
            "app",
            help="app name",
            type=str,
        )
        parser.add_argument(
            "model",
            help="model name",
            type=str,
        )
        parser.add_argument(
            "--archive_name", help=_("Name of the archive to write data to"), type=str
        )
        parser.add_argument(
            "--response",
            help=_("HttpResponse object to which the output data should be written"),
            type=HttpResponse,
        )
        parser.add_argument(
            "--ids",
            help=_("IDs of producttypes to be exported"),
            nargs="*",
            default=[],
            type=int,
        )
        parser.add_argument(
            "--exclude",
            help=_("names of fields to be excluded from the exported data"),
            nargs="*",
            default=[],
            type=str,
        )
        parser.add_argument(
            "--format",
            choices=["json", "csv"],
            default="json",
            help=_("Specify the export format: json or csv (default: json)"),
        )

    def handle(self, *args, **options):
        app = options.pop("app")
        model_name = options.pop("model")
        archive_name = options.pop("archive_name")
        response = options.pop("response")
        ids = options.pop("ids")
        exclude = options.pop("exclude")

        self.is_json = options.pop("format") == "json"

        if bool(response) == bool(archive_name):
            raise CommandError(
                _("Please use either the --archive_name or --response argument")
            )

        try:
            model = apps.get_model(app, model_name)
        except LookupError:
            raise CommandError(_("Could not find model {} {}").format(app, model_name))

        objects = self._select_and_prefetch_all(model)

        if ids:
            objects = objects.filter(id__in=ids)

        data = {}
        for producttype in objects.all():
            self._model_to_dict(producttype, data, exclude)

        if response:
            f = io.BytesIO()
            self._create_zip(f, data)
            response.content = f.getvalue()
        else:
            self._create_zip(archive_name, data)

    def _handle_foreign_key(self, instance, exclude, field, all_data):
        if field.name not in exclude:
            self._model_to_dict(
                getattr(instance, field.name),
                all_data,
                exclude + [field._related_name],
                True,
            )

    def _handle_related_objects(self, instance, meta, exclude):
        """"""
        related_instances = []

        for obj in chain(meta.related_objects):
            if obj.related_name in exclude:
                continue

            manager = getattr(instance, obj.related_name, None)

            for related_object in manager.iterator():
                related_instances.append(
                    {
                        "instance": related_object,
                        "exclude": obj.field.name,
                    }
                )

        return related_instances

    def _handle_many_to_many(
        self,
        instance,
        meta,
        exclude,
        instance_data,
        all_data,
    ):
        m2m_instances = []

        for obj in chain(meta.many_to_many):
            if obj.attname in exclude:
                continue

            manager = getattr(instance, obj.attname, None)

            if self.is_json:
                instance_data[f"{obj.attname}_ids"] = []
            else:
                table_name = f"{obj._related_name}_{obj.attname}"

                if table_name not in all_data:
                    all_data[table_name] = []

            for m2m_object in manager.iterator():
                m2m_instances.append(
                    {
                        "instance": m2m_object,
                        "exclude": obj._related_name,
                    }
                )

                if self.is_json:
                    instance_data[f"{obj.attname}_ids"].append(m2m_object.pk)
                else:
                    all_data[table_name].append(
                        {obj._related_name: instance.pk, obj.attname: m2m_object.pk}
                    )

        return m2m_instances

    def _model_to_dict(self, instance, all_data, exclude, is_fk=False):
        meta = instance._meta
        instance_data = {}

        name = str(meta.model_name)

        if name not in all_data:
            all_data[str(name)] = []
        elif any(d.get("id") == instance.id for d in all_data[name]):
            """Return if object is already added"""
            return

        for field in chain(meta.concrete_fields, meta.private_fields):
            value = field.value_from_object(instance)

            field_name = field.name
            if isinstance(field, models.ForeignKey):
                field_name = f"{field.name}_id"

            if value is not None:
                match field:
                    case models.ForeignKey():
                        self._handle_foreign_key(instance, exclude, field, all_data)
                    case models.FileField():
                        value = value.name
                    case models.UUIDField():
                        value = str(value)
                    case models.DateTimeField():
                        value = value.isoformat()
                    case models.DateField():
                        value = value.isoformat()
                    case models.DecimalField():
                        value = str(value)
                    case _:
                        pass
            instance_data[field_name] = value

        objects_to_parse = self._handle_many_to_many(
            instance, meta, exclude, instance_data, all_data
        )

        if not is_fk:
            objects_to_parse += self._handle_related_objects(instance, meta, exclude)

        all_data[name].append(instance_data)

        for obj in objects_to_parse:
            self._model_to_dict(obj["instance"], all_data, exclude + [obj["exclude"]])

    def _create_zip(self, file, results):
        for resource, data in results.items():
            with zipfile.ZipFile(file, "a") as zip_file:
                if self.is_json:
                    content = json.dumps(data)
                    ext = "json"
                else:
                    buffer = io.StringIO()
                    if data:
                        writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                    content = buffer.getvalue()
                    buffer.close()
                    ext = "csv"

                zip_file.writestr(f"{resource}.{ext}", content)

    def _select_and_prefetch_all(self, model_cls):
        select = []
        prefetch = []

        # SELECT related for ForeignKey and OneToOneField
        for field in model_cls._meta.get_fields():
            if isinstance(field, (ForeignKey, OneToOneField)) and field.related_model:
                select.append(field.name)

        # PREFETCH related for reverse and M2M fields
        for field in model_cls._meta.get_fields():
            if isinstance(field, (ManyToOneRel, ManyToManyRel)) and field.related_name:
                prefetch.append(field.related_name)

        return model_cls.objects.select_related(*select).prefetch_related(*prefetch)
