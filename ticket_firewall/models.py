from utilities.choices import ChoiceSet
from django.db import models
from netbox.models import NetBoxModel
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.dispatch import receiver
import os
from ipam.models import Prefix, IPAddress
from dcim.models import Device



class Ticket_status(ChoiceSet):
    key = 'Ticket.status'
    active = 'active'
    inactive = 'inactive'
    staged = 'staged'
    CHOICES = [
        (active, 'Active', 'green'),
        (inactive, 'Inactive', 'red'),
        (staged, 'Staged', 'orange'),
    ]

class Rule_Action(ChoiceSet):
    key = 'Rule.action'
    CHOICES = [
        ('', '----', 'white'),
        ('permit', 'Permit', 'green'),
        ('deny', 'Deny', 'red'),
        ('delete', 'Delete', 'blue'),
        ('reject', 'Reject', 'orange'),
    ]


class Ticket(NetBoxModel):
    ticket_id = models.PositiveIntegerField(
        unique=True
    )
    ticket_name = models.CharField(
        max_length=100,
        unique=True,
        blank=True
    )
    id_directum = models.CharField(
        max_length=100,
        blank=True
    )
    status = models.CharField(
        max_length=30,
        choices=Ticket_status,
        default=Ticket_status.inactive
    )
    description = models.CharField(
        max_length=500,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )
    clone_fields = (
        'ticket_id', 'ticket_name', 'id_directum', 'status', 'description', 'comments'
    )


    class Meta:
        ordering = ('ticket_id',)
    # it returns RuleTable
    def __str__(self):
        return str(self.ticket_id)
    def get_status_color(self):
        return Ticket_status.colors.get(self.status)
    def get_absolute_url(self):
        return reverse('plugins:ticket_firewall:ticket', args=[self.pk])


fs = FileSystemStorage(location='./media/ticket_attachments')
class AttachFile(NetBoxModel):
    ticket_id = models.ForeignKey(
        to=Ticket,
        on_delete= models.CASCADE,
        related_name='file'
    )
    file = models.FileField(storage=fs)
    name = models.CharField(
        max_length=500,
        blank=True
    )
    def __str__(self):
        return f'{self.ticket_id.ticket_id}: {self.file.name}'
    def get_absolute_url(self):
        return reverse('plugins:ticket_firewall:ticket', args=[self.ticket_id.id])

    @property
    def size(self):
        """
        Wrapper around `image.size` to suppress an OSError in case the file is inaccessible. Also opportunistically
        catch other exceptions that we know other storage back-ends to throw.
        """
        expected_exceptions = [OSError]
        try:
            from botocore.exceptions import ClientError
            expected_exceptions.append(ClientError)
        except ImportError:
            pass
        try:
            return self.file.size
        except tuple(expected_exceptions):
            return None



class Protocol(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Rule(NetBoxModel):
    ticket_id = models.ForeignKey(
        to=Ticket,
        on_delete=models.CASCADE,
        related_name='rules'
    )
    index = models.PositiveIntegerField() 

    
    
    source_prefix = models.ManyToManyField(Prefix, blank=True, related_name="+")
    source_address = models.ManyToManyField(IPAddress, blank=True, related_name="+")
    source_ports = models.CharField(
        max_length=100,
        blank=True,
        default='Any'
    )

    destination_prefix = models.ManyToManyField(Prefix, blank=True, related_name="+")
    destination_address = models.ManyToManyField(IPAddress, blank=True, related_name="+")
    protocols = models.ManyToManyField(Protocol, blank=True, related_name="+" )
    firewall = models.ManyToManyField(Device, blank=True, related_name="+",)

    destination_ports = models.CharField(
        max_length=100,
        blank=True,
        default='Any'
    )


    action = models.CharField(max_length=30, choices=Rule_Action, blank=True, default='permit')

    description = models.CharField(max_length=500, blank=True)

    opened = models.DateField(blank=True, null=True, verbose_name='Opening date')

    closed = models.DateField(blank=True, null=True, verbose_name='Closing date')



    clone_fields = (
        'ticket_id', 'source_ports', 'destination_ports', 'protocols', 'action', 'description', 'opened', 'closed','source_prefix', 'destination_prefix', 'firewall'
    )

    class Meta:
        ordering = ('ticket_id', 'index')
        unique_together = ('ticket_id', 'index')

    def __str__(self):
        return f'Ticket {self.ticket_id}: Rule {self.index}'

    def get_action_color(self):
        return Rule_Action.colors.get(self.action)

    def get_absolute_url(self):
        return reverse('plugins:ticket_firewall:rule', args=[self.pk])

    def __unicode__(self): 
        return self


# these receivers delete the file from the file system. Without them, the record will only be deleted from the Database
@receiver(models.signals.post_delete, sender=AttachFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
            reverse('plugins:ticket_firewall:ticket', args=[instance.pk])


@receiver(models.signals.pre_save, sender=AttachFile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file
    except sender.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
