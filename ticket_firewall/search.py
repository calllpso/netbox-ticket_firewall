from netbox.search import SearchIndex
from .models import Ticket, Rule

class TicketIndex(SearchIndex):
    model = Ticket
    fields = (
        ('ticket_id', 100),
        ('ticket_name', 200),
        ('id_directum', 100),
        ('status', 100),
        ('description', 500),
        ('comments', 5000),
    )

class RuleIndex(SearchIndex):
    model = Rule
    fields = (
        ('action', 100),
        ('source_prefix'      , 100),
        ('source_address'     , 100), 
        ('source_ports'       , 100), 
        ('destination_prefix' , 100), 
        ('destination_address', 100), 
        ('destination_ports'  , 100), 
        ('protocols'           , 100), 
        ('action'             , 100), 
        ('device'             , 100), 
        ('description'        , 100), 
        ('opened'             , 100), 
        ('closed'             , 100), 
    )
    
indexes = [TicketIndex, RuleIndex]
