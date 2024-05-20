from netbox.forms import NetBoxModelForm,NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField,TagFilterField, DynamicModelMultipleChoiceField
from utilities.forms.widgets import *
from .models import Ticket, Rule, Rule_Action, Ticket_status, AttachFile, Protocol
from django import forms
from django.db.models import Max
from ipam.models import Prefix, IPAddress
from dcim.models import Device
from netbox.forms import NetBoxModelImportForm



class AttachFileForm(NetBoxModelForm):
    file = forms.FileField()
    ticket_id = DynamicModelChoiceField(
        queryset=Ticket.objects.all()
    )
    def __init__(self, *args, **kwargs):
        super(AttachFileForm,self).__init__(*args, **kwargs)

        if 'ticket_id' in kwargs:
            ticket_id = kwargs.pop('ticket_id')
            self.fields['ticket_id'].initial = ticket_id
    
    class Meta:
        model = AttachFile
        fields = ('ticket_id','name', 'file',)

class TicketFormCreate(NetBoxModelForm):
    comments = CommentField()
    class Meta:
        model = Ticket
        fields = ('ticket_id', 'ticket_name', 'status', 'id_directum', 'tags', 'description', 'comments')

    def __init__(self, *args, **kwargs):
        super(TicketFormCreate,self).__init__(*args, **kwargs)
        try:
            max_index=Ticket.objects.filter().aggregate(max_index=Max('ticket_id'))
            ticket_id = max_index['max_index'] + 1
            ticket_id = int(max_index['max_index']) + 1
            self.initial['ticket_id'] = ticket_id
        except:
            pass

class TicketFormEdit(NetBoxModelForm):
    comments = CommentField()
    class Meta:
        model = Ticket
        fields = ('ticket_id', 'ticket_name', 'status', 'id_directum', 'tags', 'description', 'comments')

class RuleFormEdit(NetBoxModelForm):
    ticket_id = DynamicModelChoiceField(
        queryset=Ticket.objects.all()
    )

    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )

    source_address = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False
    )

    destination_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )

    destination_address = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False
    )

    protocols = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple, 
        queryset = Protocol.objects.all(),
        required=False
    )

    device = DynamicModelMultipleChoiceField(
        queryset = Device.objects.all(),
        required=False,
        selector = True
    )


    class Meta:
        model = Rule
        fields = (
            'ticket_id', 'index', 'device',
            'source_prefix', 'source_address', 'source_ports',  
            'destination_prefix', 'destination_address', 'destination_ports', 
            'protocols', 'action', 'opened', 'closed',  'description', 'tags',  
        )
        widgets = {
            'opened': DatePicker(),
            'closed': DatePicker()
        }

class RuleFormCreate(NetBoxModelForm):
    ticket_id = DynamicModelChoiceField(
        queryset=Ticket.objects.all()
    )

    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )

    source_address = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False
    )

    destination_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False
    )

    destination_address = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False
    )

    protocols = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple, 
        queryset = Protocol.objects.all(),
        required=False
    )
             
    device = DynamicModelMultipleChoiceField(
        queryset = Device.objects.all(),
        required=False,
        selector = True
    )

    class Meta:
        model = Rule
        fields = (
            'ticket_id', 'index', 
            'source_prefix', 'source_address', 'source_ports',  
            'destination_prefix', 'destination_address', 'destination_ports', 
            'protocols', 'action', 'device', 'opened', 'closed', 'description', 'tags',  
        )
        widgets = {
            'opened': DatePicker(),
            'closed': DatePicker()
        }

class RuleFilterForm(NetBoxModelFilterSetForm):
    model = Rule

    ticket_id = DynamicModelChoiceField(
        queryset=Ticket.objects.all(),
        required=False
    )
    index = forms.ModelChoiceField(
        widget = forms.Select, 
        queryset = Rule.objects.values_list('index', flat =True),
        required=False
    )

    source_prefix = forms.ModelChoiceField(
        widget = forms.Select, 
        queryset=Prefix.objects.all(),
        required=False
    )

    source_address = forms.ModelChoiceField(
        widget = forms.Select, 
        queryset=IPAddress.objects.all(),
        required=False
    )

    source_ports = forms.ModelChoiceField(
        widget = forms.Select, 
        queryset = Rule.objects.values_list('source_ports', flat =True),
        required=False
    )

    destination_prefix = forms.ModelMultipleChoiceField (
        widget = forms.SelectMultiple,
        queryset=Prefix.objects.all(),
        required=False
    )

    destination_address = forms.ModelMultipleChoiceField (
        widget = forms.SelectMultiple,
        queryset=IPAddress.objects.all(),
        required=False
    )
    
    destination_ports = forms.ModelChoiceField(
        widget = forms.Select, 
        queryset = Rule.objects.values_list('destination_ports', flat =True),
        required=False
    )

    protocols = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple, 
        queryset = Protocol.objects.all(),
        required=False
    )

    action = forms.ChoiceField(
        choices=Rule_Action,
        widget = forms.Select,
        required=False
    )

    opened = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple,
        queryset=Rule.objects.values_list('opened', flat =True).exclude(opened=None),
        required=False
    )

    closed = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple,
        queryset=Rule.objects.values_list('closed', flat =True).exclude(closed=None),
        required=False
    )

    device = DynamicModelMultipleChoiceField(
        queryset = Device.objects.all(),
        required=False
    )
    
    tag = TagFilterField(model)


class TicketFilterForm(NetBoxModelFilterSetForm):
    model = Ticket
    tag = TagFilterField(model)
    ticket_id = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple, 
        queryset=Ticket.objects.values_list('ticket_id', flat =True),
        required=False
        )

    ticket_name = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple, 
        queryset=Ticket.objects.values_list('ticket_name', flat =True),
        required=False
        )

    id_directum = forms.ModelMultipleChoiceField(
        widget = forms.SelectMultiple, 
        queryset=Ticket.objects.values_list('id_directum', flat =True),
        required=False
        )
        
    status = forms.MultipleChoiceField(
        widget = forms.SelectMultiple, 
        choices=Ticket_status,
        required=False
    )

class TicketCSVForm(NetBoxModelImportForm):
    class Meta:
        model = Ticket
        fields = ('ticket_id', 'ticket_name', 'id_directum', 'status', 'description', 'comments',)
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        

class RuleCSVForm(NetBoxModelImportForm):
    from taggit.models import Tag
    taggg = Tag.objects.all()

    class Meta:
        model = Rule

        fields = ('ticket_id', 'index', 
            'source_prefix', 'source_address', 'source_ports',  
            'destination_prefix', 'destination_address', 'destination_ports', 
            'protocols', 'action', 'device',  'opened', 'closed', 'description', 'tags',)
            
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

class UploadFileForm(forms.Form):
    file = forms.FileField()
