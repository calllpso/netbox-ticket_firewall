import django_tables2 as tables
from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import Ticket, Rule

# pk and actions columns render the checkbox selectors and dropdown menus
class TicketTable(NetBoxTable):
    ticket_id = tables.Column(linkify=True)
    status = ChoiceFieldColumn()
    rule_count = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Ticket
        fields = ('pk', 'id', 'ticket_id', 'ticket_name', 'rule_count', 'status', 'id_directum', 'actions', 'description', 'comments', 'created')
        default_columns = ('ticket_id', 'ticket_name', 'id_directum', 'rule_count', 'status', 'description', 'created')
        ticket_id = tables.Column(linkify=True)
        status = ChoiceFieldColumn()


class RuleTable(NetBoxTable):
    ticket_id = tables.Column(linkify=True)
    index = tables.Column(linkify=True)
    source_prefix = tables.ManyToManyColumn(linkify_item =True)
    source_address = tables.ManyToManyColumn(linkify_item =True)
    destination_prefix = tables.ManyToManyColumn(linkify_item =True)
    destination_address = tables.ManyToManyColumn(linkify_item =True)
    
    device = tables.ManyToManyColumn(linkify_item =True)

    ### цвет
    action = ChoiceFieldColumn()

    class Meta(NetBoxTable.Meta):
        model = Rule
        fields = (
            'pk', 'id', 'ticket_id', 'index', 
            'source_prefix', 'source_address', 'source_ports',
            'destination_prefix', 'destination_address', 'destination_ports', 
            'protocols', 'action', 'device', 'description', 'opened', 'closed', 
        )
        default_columns = (
            'ticket_id', 'index', 
            'source_prefix', 'source_address', 'source_ports',
            'destination_prefix', 'destination_address', 'destination_ports', 
            'protocols', 'action', 'device', 'opened', 'closed', 
        )
