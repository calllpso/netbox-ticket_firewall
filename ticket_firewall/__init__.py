from netbox.plugins import PluginConfig     #4v version


class NetBox_TicketsListsConfig(PluginConfig):
    name = 'ticket_firewall'
    verbose_name = 'Firewall Tickets'
    description = ''
    version = '1.2.1'
    base_url = 'ticket-firewall'

config = NetBox_TicketsListsConfig
