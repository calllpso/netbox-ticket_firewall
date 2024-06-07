from netbox.views import generic
from django.db.models import Count
from . import forms, models, tables, filtersets
from django.http import HttpResponse
from django.shortcuts import  render
import io,pandas,numpy
from datetime import datetime
from contextlib import suppress
from .models import Protocol, Rule_Action
import datetime
from utilities.views import ViewTab, register_model_view
from django.db.models import Q

from ipam.models import Prefix, IPAddress

status_continue = ''
rule_errors = ''

#FILES
class AttachFileEditView(generic.ObjectEditView):
    queryset = models.AttachFile.objects.all()
    form = forms.AttachFileForm
class AttachFileDeleteView(generic.ObjectDeleteView):
    queryset = models.AttachFile.objects.all()


#TICKETS
class TicketView(generic.ObjectView):
    queryset = models.Ticket.objects.all()
    template_name = 'ticket_firewall/ticket.html'
    def get_extra_context(self, request, instance):
        table = tables.RuleTable(instance.rules.all())
        table.configure(request)
        files = models.AttachFile.objects.filter(ticket_id = instance)
        next_rule_index = instance.rules.count() + 1
        return {
            'next_rule_index': next_rule_index,
            'files':    files,
            'rules_table': table,
        }
class TicketListView(generic.ObjectListView):
    queryset = models.Ticket.objects.annotate(
        rule_count=Count('rules')
    )
    table = tables.TicketTable
    filterset = filtersets.TicketFilterSet
    filterset_form = forms.TicketFilterForm

class TicketCreateView(generic.ObjectEditView):
    queryset = models.Ticket.objects.all() 
    form = forms.TicketFormCreate

class TicketEditView(generic.ObjectEditView):
    queryset = models.Ticket.objects.all()
    form = forms.TicketFormEdit

class TicketDeleteView(generic.ObjectDeleteView):
    queryset = models.Ticket.objects.all()

#RULES
class RuleView(generic.ObjectView):
    queryset = models.Rule.objects.all()
    def get_extra_context(self, request, instance):
        protocols = instance.protocols.all()
        source_prefix = instance.source_prefix.all()
        source_address = instance.source_address.all()
        destination_prefix = instance.destination_prefix.all()
        destination_address = instance.destination_address.all()
        firewall = instance.firewall.all()
        return {
            'protocols': protocols,
            'source_prefix': source_prefix,
            'source_address': source_address,
            'destination_prefix': destination_prefix,
            'destination_address': destination_address,
            'firewall': firewall
        }
    



class RuleListChildView(generic.ObjectChildrenView):
    child_model = models.Rule
    table = tables.RuleTable
    filterset = filtersets.RuleFilterSet
    template_name = "inc/view_tab.html"

@register_model_view(IPAddress, "rules")
class SourceIPAddressRuleListView(RuleListChildView):
    queryset = IPAddress.objects.prefetch_related("tags")
    tab = ViewTab(
        label="Rules",
    )
    def get_children(self, request, parent):
        qs_filter = Q(source_address=parent) | Q(destination_address=parent)
        return self.child_model.objects.all().filter(qs_filter)


class RuleListChildView(generic.ObjectChildrenView):
    child_model = models.Rule
    table = tables.RuleTable
    filterset = filtersets.RuleFilterSet
    template_name = "inc/view_tab.html"

@register_model_view(Prefix, "rules")
class SourceIPAddressRuleListView(RuleListChildView):
    queryset = Prefix.objects.prefetch_related("tags")
    tab = ViewTab(
        label="Rules",
    )
    def get_children(self, request, parent):
        qs_filter = Q(source_prefix=parent) | Q(destination_prefix=parent)
        return self.child_model.objects.all().filter(qs_filter)


class RuleListView(generic.ObjectListView):
    queryset = models.Rule.objects.all()
    table = tables.RuleTable
    filterset = filtersets.RuleFilterSet
    filterset_form = forms.RuleFilterForm
    actions = {
    'add': {'add'},
    'import': {'add'},
    'export': set(),
    'bulk_edit': {'change'},
    'bulk_delete': {'delete'},
}

class RuleCreateView(generic.ObjectEditView):
    queryset = models.Rule.objects.all()
    form = forms.RuleFormCreate

class RuleEditView(generic.ObjectEditView):
    queryset = models.Rule.objects.all()
    form = forms.RuleFormEdit

class RuleDeleteView(generic.ObjectDeleteView):
    queryset = models.Rule.objects.all()

# IMPORT
class TicketBulkImportView(generic.BulkImportView):
    queryset = models.Ticket.objects.all()
    model_form = forms.TicketCSVForm
    table = tables.TicketTable ####

# defs for import Rules _____________________
def date_or_none(val):
    str_time = str(val)
    if 'one' in str_time:
        return None
    try:
        result = pandas.to_datetime(str_time).date()       
        return result
    except Exception as e:
        return e    
def filter_list(field, value_list):
    fltr = ''
    for i in value_list:
        fltr = f"{fltr}.filter({field}={i})"
    return fltr
def set_rule_field(rule, field, value_list):
    for i in value_list:
        with suppress(ValueError):
            eval(f'rule.{field}.add({i})')

def get_list_field_id(values, model, model_field):
    list_additional_objects = []
    for i in values:
        getted_objects = eval(f'{model}.objects.all().filter({model_field} = "{str(i)}")')
        if len(getted_objects)!=0:
            if model in ["Prefix", "IPAddress"]:
                getted_objects = getted_objects.filter(vrf=None, status='active')
                if len(getted_objects)==0:
                    try:
                        additional_object = eval(f'{model}.objects.create({model_field} = "{str(i)}")')
                    except Exception as e:
                        return e
                else:
                    additional_object = getted_objects[0]
            else:
                if len(getted_objects)==0:
                    try:
                        additional_object = eval(f'{model}.objects.create({model_field} = "{str(i)}")')
                    except Exception as e:
                        return e
                else:
                    additional_object = getted_objects[0]
        else:
            try:
                additional_object = eval(f'{model}.objects.create({model_field} = "{str(i)}")')
            except Exception as e:
                return e
        print(additional_object)
        list_additional_objects.append(additional_object.id)
    return list_additional_objects
#________________________


def list_check(value_list_id, field_for_error):
    if type(value_list_id)!=list:
        global status_continue
        status_continue = False
        rule_error = {'error': f'{field_for_error} {str(value_list_id)}'}
        global rule_errors
        rule_errors.append(rule_error)

def check_date(value_date):
    if not isinstance(value_date,datetime.date) and value_date != None:
        global rule_errors
        rule_error = {'error': f'opened {str(value_date)}'}
        rule_errors.append(rule_error)

# ValueError: NaTType does not support utcoffset: if empty place (!None)
def RuleImport(request):
    form = forms.UploadFileForm(request.POST, request.FILES)
    # File for UI
    if request.method == 'POST':
        if request.content_type == 'multipart/form-data':
            try:
                file_content_type = request.FILES['myfile'].content_type
            except:
                return HttpResponse(f'<h> error: file is required </h>')
            if file_content_type == 'text/csv':
                common_errors = []
                already_added_rules = []
                success_added_rules = 0
                
                str_text = ''
                for line in request.FILES['myfile']:
                    str_text = str_text + line.decode()
                df = pandas.read_csv(io.StringIO(str_text), sep=";")
                for rule in df.iloc:
                    global rule_errors
                    rule_errors = []
                    global status_continue 
                    status_continue = True

                    try:
                        ticket = models.Ticket.objects.get(ticket_id = rule['ticket_id'])
                    except Exception as e:
                        rule_error = {'error': f'ticket_id {str(e)}'}
                        rule_errors.append(rule_error)
                        common_errors.append({'rule': rule,'rule_errors': rule_errors})
                        continue
                    
                    #NaN
                    def checkNone(values):
                        if type(values) == numpy.float64:
                            return ''
                        else:
                            return values
                    
                    source_prefix_list       = checkNone(rule['source_prefix'])
                    source_address_list      = checkNone(rule['source_address'])
                    destination_prefix_list  = checkNone(rule['destination_prefix'])
                    destination_address_list = checkNone(rule['destination_address'])
                    protocol_list            = checkNone(rule['protocols'])
                    
                    # filter(None  - filtering, excluding None)  
                    source_prefix_list_id       = get_list_field_id(list(filter(None,source_prefix_list.strip().split(','))), 'Prefix', 'prefix')
                    source_address_list_id      = get_list_field_id(list(filter(None,source_address_list.strip().split(','))), 'IPAddress', 'address')
                    destination_prefix_list_id  = get_list_field_id(list(filter(None,destination_prefix_list.strip().split(','))), 'Prefix', 'prefix')
                    destination_address_list_id = get_list_field_id(list(filter(None,destination_address_list.strip().split(','))), 'IPAddress', 'address')
                    protocol_list_id            = get_list_field_id(list(filter(None,protocol_list.strip().split(','))), 'Protocol', 'name')
                    
                    opened  = date_or_none(rule['opening_date'])
                    closed  = date_or_none(rule['closing_date']) 
                    check_date(opened)
                    check_date(closed)
                    list_check(source_prefix_list_id,'source_prefix')
                    list_check(source_address_list_id,'source_address')
                    list_check(destination_address_list_id,'destination_address')
                    list_check(destination_prefix_list_id,'destination_prefix')
                    list_check(protocol_list_id,'protocols')

                    action = [item for item in Rule_Action.CHOICES if item[0] == rule['action']]
                    if len(action)==0:
                        rule_error = {'error': f'action {rule["action"]}'}
                        rule_errors.append(rule_error)

                    if len(rule_errors) !=0:
                        common_errors.append({'rule': rule,'rule_errors': rule_errors})
                        continue
                    filter_str = filter_list('source_prefix',source_prefix_list_id) \
                        + filter_list('source_address',source_address_list_id) \
                        + filter_list('destination_prefix',destination_prefix_list_id) \
                        + filter_list('destination_address',destination_address_list_id) \
                        + filter_list('protocols',protocol_list_id)
                    search_match_rule = eval(f'models.Rule.objects.all(){filter_str}').filter(ticket_id = ticket)
                    
                    if not search_match_rule.count():
                        new_rule = models.Rule.objects.create(
                        ticket_id_id      = ticket.id,
                        index             = ticket.rules.count() + 1,
                        source_ports      = rule['source_ports'],
                        destination_ports = rule['destination_ports'],
                        action            = rule['action'],
                        opened            = opened,
                        closed            = closed 
                        )

                        set_rule_field(new_rule, 'source_prefix',source_prefix_list_id)
                        set_rule_field(new_rule, 'source_address',source_address_list_id)
                        set_rule_field(new_rule, 'destination_prefix',destination_prefix_list_id)
                        set_rule_field(new_rule, 'destination_address',destination_address_list_id)
                        set_rule_field(new_rule, 'protocols',protocol_list_id)
                        new_rule.save()
                        success_added_rules+=1
                    else:
                        already_added_rules.append(rule)

                resp = {'1 errors': common_errors,   
                    '2 already_added_rules': already_added_rules, 
                    '3 number success_added_rules': success_added_rules,
                    }
                # debug_info = 'str_text'
                return render(request, 'ticket_firewall/rule_import.html', {'form': form, 'resp': resp})
            else:
                return render(request, 'ticket_firewall/rule_import.html', {'form': form, 'resp': {'error': 'csv file format'}})  
    else:
        form = forms.UploadFileForm()
    return render(request, 'ticket_firewall/rule_import.html', {'form': form})