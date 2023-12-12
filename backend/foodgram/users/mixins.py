from rest_framework import mixins, viewsets


class ListCreateRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet для методов Get, List, Create, Retrieve."""

    lookup_field = 'id'
