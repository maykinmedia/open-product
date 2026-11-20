from pathlib import Path

from django.conf import settings

from celery import Celery, bootsteps
from celery.signals import worker_ready, worker_shutdown
from django_structlog.celery.steps import DjangoStructLogInitStep
from maykin_common.logging.celery import setup_celery_structlog

from openproduct.setup import setup_env

setup_env()

app = Celery("openproduct")
app.config_from_object("django.conf:settings", namespace="CELERY")
setup_celery_structlog(format_exc_info=settings.LOG_FORMAT_CONSOLE == "json")

assert app.steps is not None
app.steps["worker"].add(DjangoStructLogInitStep)

app.autodiscover_tasks()

HEARTBEAT_FILE = Path(settings.BASE_DIR) / "tmp" / "celery_worker_heartbeat"
READINESS_FILE = Path(settings.BASE_DIR) / "tmp" / "celery_worker_ready"


#
# Utilities for checking the health of celery workers
#
class LivenessProbe(bootsteps.StartStopStep):
    requires = ("celery.worker.components:Timer",)

    def __init__(self, worker, **kwargs):
        self.requests = []
        self.tref = None

    def start(self, parent):
        self.tref = parent.timer.call_repeatedly(
            10.0,
            self.update_heartbeat_file,
            (parent,),
            priority=10,
        )

    def stop(self, parent):
        HEARTBEAT_FILE.unlink(missing_ok=True)

    def update_heartbeat_file(self, worker):
        HEARTBEAT_FILE.touch()


@worker_ready.connect
def create_readiness_file(**_):
    READINESS_FILE.touch()


@worker_shutdown.connect
def remove_readiness_file(**_):
    READINESS_FILE.unlink(missing_ok=True)


app.steps["worker"].add(LivenessProbe)
