from rest_framework.routers import DefaultRouter

from openproduct.locaties.viewsets import (
    ContactViewSet,
    LocatieViewSet,
    OrganisatieViewSet,
)

LocatieRouter = DefaultRouter(trailing_slash=False)

LocatieRouter.register("locaties", LocatieViewSet, basename="locatie")
LocatieRouter.register("organisaties", OrganisatieViewSet, basename="organisatie")
LocatieRouter.register("contacten", ContactViewSet, basename="contact")
