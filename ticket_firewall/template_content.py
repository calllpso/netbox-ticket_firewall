from netbox.plugins import PluginTemplateExtension
from .models import Rule

class PrefixRulesExtension(PluginTemplateExtension):
    model = 'ipam.prefix'
    def detail_tabs(self):
        prefix = self.context['object']
        source_prefix_rules = Rule.objects.all().filter(source_prefix = prefix.id)
        destination_prefix_rules = Rule.objects.all().filter(destination_prefix = prefix.id)

        return self.render('ticket_firewall/prefix_extension.html', extra_context={
            "source_prefix_rules":  source_prefix_rules,
            "destination_prefix_rules":  destination_prefix_rules,
            })

    def buttons(self):
        prefix = self.context['object']
        return self.render(
            "ticket_firewall/prefix_extension_buttons.html",
            extra_context={ "prefix": prefix, },
        )

class IPAddressRulesExtension(PluginTemplateExtension):
    model = 'ipam.ipaddress'

    def right_page(self):
        ipaddress = self.context['object']
        source_address_rules = Rule.objects.all().filter(source_address = ipaddress.id)
        destination_address_rules = Rule.objects.all().filter(destination_address = ipaddress.id)

        return self.render('ticket_firewall/ip_extension.html', extra_context={
            "source_address_rules":  source_address_rules,
            "destination_address_rules":  destination_address_rules,
            })

    def buttons(self):
        ipaddress = self.context['object']
        return self.render(
            "ticket_firewall/ip_extension_buttons.html",
            extra_context={ "ipaddress": ipaddress, },
        )

template_extensions = [PrefixRulesExtension, IPAddressRulesExtension]
