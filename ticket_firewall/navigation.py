from netbox.plugins import PluginMenu, PluginMenuItem, PluginMenuButton
from django.conf import settings

plugin_settings = settings.PLUGINS_CONFIG["ticket_firewall"]

menu_buttons = (
    PluginMenuItem(
        link='plugins:ticket_firewall:ticket_list',
        link_text='Tickets',
        buttons=(PluginMenuButton(
                link="plugins:ticket_firewall:ticket_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
            ),
        ), 
    ),
    PluginMenuItem(
        link='plugins:ticket_firewall:rule_list',
        link_text='Ticket Rules',
    ),
)

if plugin_settings.get("top_level_menu"):
    menu = PluginMenu(
        label="Firewall Tickets",
        groups=(("", menu_buttons),),
        icon_class="mdi mdi-lock",
    )
else:
    menu_items = menu_buttons