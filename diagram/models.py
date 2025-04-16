from django.db import models
import uuid
from account.models import UserAccount
from .choices import VisibilityChoices, DatabaseTypeChoices, RelationshipTypeChoices
from dateutil.relativedelta import relativedelta
from django.utils import timezone

class Diagram(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='diagrams')
    visibility = models.CharField(choices=VisibilityChoices.choices, default=VisibilityChoices.PUBLIC, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    database_type = models.CharField(choices=DatabaseTypeChoices.choices, default=DatabaseTypeChoices.POSTGRESQL, max_length=20)
    synced = models.BooleanField(default=True)
    writer = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagramwrites')
    live_sync =models.BooleanField(default=False)
    pay_per_diagram = models.BooleanField(default=False)
    amount_paid = models.IntegerField(default=0)
    has_paid = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

# class Version(models.Model):
#     diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE)
#     version_number = models.IntegerField(default=1)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
class DiagramMember(models.Model):
    user= models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    

class DiagramInvitationStatusChoices(models.TextChoices):
    PENDING= 'pending', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'

class DiagramInvitation(models.Model):
    email = models.EmailField()
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)    
    expiry_date = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)
    status = models.CharField(choices=DiagramInvitationStatusChoices.choices, default=DiagramInvitationStatusChoices.PENDING)
    
    @property
    def get_expiry_date(self):
        if self.created_at:
            return self.created_at + relativedelta(days=7)
        else:
            return timezone.now() + relativedelta(days=7)
    
    @property
    def is_active(self):
        return timezone.now() < self.get_expiry_date
        
    def save(self, *args, **kwargs):
        self.expiry_date = self.get_expiry_date
        super().save(*args, **kwargs)
        
        
class DatabaseTable(models.Model):
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)
    comment = models.TextField(null=True, blank=True)
    x_position = models.FloatField()
    y_position = models.FloatField()
    description = models.TextField(null=True, blank=True)    
    synced = models.BooleanField(default=True)
    flow_id = models.IntegerField(default=-1)#id that will be used to identify this items on react flow
    
    
    def __str__(self):
        return f"{self.id} - {self.name}"

class DatabaseColumn(models.Model):
    db_table = models.ForeignKey(DatabaseTable, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    datatype = models.CharField(max_length=50)
    is_primary_key = models.BooleanField(default=False)
    is_nullable = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    default_value = models.CharField(max_length=255, null=True, blank=True)
    synced = models.BooleanField(default=True)
    flow_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"({self.id} - {self.name} - {self.datatype}) on {self.db_table.name}"    
    
    class Meta:
        ordering = ['-created_at']

class Relationship(models.Model):
    diagram = models.ForeignKey(Diagram, on_delete=models.CASCADE)
    from_column = models.ForeignKey(DatabaseColumn, on_delete=models.CASCADE, related_name='from_column_rels')
    to_column = models.ForeignKey(DatabaseColumn, on_delete=models.CASCADE, related_name="to_column_rels")
    rel_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    synced = models.BooleanField(default=True)
    source_suffix = models.CharField(max_length=10, default='ls')
    target_suffix = models.CharField(max_length=10, default='rt')
    from_rel = models.CharField(max_length=6, choices=RelationshipTypeChoices.choices, default=RelationshipTypeChoices.ONE)
    to_rel = models.CharField(max_length=6, choices=RelationshipTypeChoices.choices, default=RelationshipTypeChoices.ONE)
    
    
    