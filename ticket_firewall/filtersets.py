from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import MultiValueCharFilter
from .models import Rule, Ticket
from django.db.models import Q


class RuleFilterSet(NetBoxModelFilterSet):
    source_prefix = MultiValueCharFilter()
    destination_prefix =  MultiValueCharFilter()
    source_ports =  MultiValueCharFilter()
    destination_ports =  MultiValueCharFilter()
    class Meta:
        model = Rule
        fields = ('ticket_id', 'index', 
        'source_prefix', 'source_address', 'source_ports',
        'destination_prefix', 'destination_address', 'destination_ports',
        'protocols', 'action', 'opened', 'closed',)
    def search(self, queryset, name, value):
        qs_filter = Q(ticket_id__ticket_id__contains=value) | Q(index__contains=value)  |\
        Q(source_prefix__prefix__contains=value) | Q(source_address__address__contains=value) | Q(source_ports__contains=value) |\
        Q(destination_prefix__prefix__contains=value) | Q(destination_address__address__contains=value) | Q(destination_ports__contains=value) | \
        Q(protocol__name__contains=value) |  Q(action__contains=value) | Q(opened__icontains=value) | Q(closed__contains=value)
        return queryset.filter(qs_filter).order_by('id').distinct('id')     

class TicketFilterSet(NetBoxModelFilterSet):
    status =  MultiValueCharFilter()    #for filter (not quick search)
    class Meta:
        model = Ticket
        fields = ('ticket_id', 'ticket_name', 'id_directum', 'status')
    def search(self, queryset, name, value):
        qs_filter = Q(ticket_id__contains=value) | Q(ticket_name__contains=value) | Q(id_directum__contains=value) | Q(status__contains=value)
        return queryset.filter(qs_filter)

