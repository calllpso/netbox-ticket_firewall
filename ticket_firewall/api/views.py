from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets, models
from .serializers import TicketSerializer, RuleSerializer


class TicketViewSet(NetBoxModelViewSet):
    queryset = models.Ticket.objects.all()
    serializer_class = TicketSerializer
    filterset_class = filtersets.TicketFilterSet

class RuleViewSet(NetBoxModelViewSet):
    queryset = models.Rule.objects.all()
    serializer_class = RuleSerializer
    filterset_class = filtersets.RuleFilterSet
