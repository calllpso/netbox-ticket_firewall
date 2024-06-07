from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import Ticket, Rule,AttachFile, Protocol
from netbox.api.serializers import WritableNestedSerializer
from ipam.api.serializers import PrefixSerializer, IPAddressSerializer
from dcim.api.serializers import DeviceSerializer

class NestedTicketSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ticket_firewall-api:ticket-detail'
    )
    class Meta:
        model = Ticket
        fields = ['url', 'ticket_name']

class TicketSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ticket_firewall-api:ticket-detail'
    )
    rule_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Ticket
        fields = ['url', 'rule_count', 'ticket_name']
class AttachFileSerializer(NetBoxModelSerializer):
    ticket_id = NestedTicketSerializer()
    class Meta:
        model = AttachFile
        fields = ['name', 'ticket_id']
class ProtocolSerializer(NetBoxModelSerializer):
    class Meta:
        model = Protocol
        fields = ['name']

class RuleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:ticket_firewall-api:rule-detail'
    )
    ticket_id = NestedTicketSerializer()
    protocols = ProtocolSerializer(many=True, read_only=True, nested=True)

    source_prefix = PrefixSerializer(many=True, read_only=True, nested=True)
    source_address = IPAddressSerializer(many=True, read_only=True, nested=True)
    destination_prefix = PrefixSerializer(many=True, read_only=True, nested=True)
    destination_address = IPAddressSerializer(many=True, read_only=True, nested=True)
    firewall = DeviceSerializer(many=True, read_only=True, nested=True)
    
    
    class Meta:
        model = Rule 
        fields = ['url', 'ticket_id', 'protocols', 'source_prefix', 'source_address', 'source_address', 'destination_prefix', 'destination_address', 'firewall']
