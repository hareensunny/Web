import os
from django.db import models, transaction
from django.utils.html import mark_safe
from datetime import datetime
from datetime import time
from django.core.validators import MinValueValidator, MaxValueValidator

class WBS(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Factory(models.Model):
    name = models.CharField(max_length=100)
    wbs = models.ForeignKey(WBS, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class BU(models.Model):
    name = models.CharField(max_length=100)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    bu = models.ForeignKey(BU, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ProjectGroup(models.Model):
    name = models.CharField(max_length=100)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Requestor(models.Model):
    name = models.CharField(max_length=100)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Litho(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Reticle(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Integrator(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class RequestType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Lot(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    wbs = models.ForeignKey(WBS, on_delete=models.CASCADE)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    bu = models.ForeignKey(BU, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)
    requestor = models.ForeignKey(Requestor, on_delete=models.CASCADE)
    # photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    reticle = models.ForeignKey(Reticle, on_delete=models.CASCADE)
    litho = models.ForeignKey(Litho, on_delete=models.CASCADE)
    integrator = models.ForeignKey(Integrator, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    special_focus = models.CharField(max_length=100)
    request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE)
    estimated_end_date = models.DateField()
    no_of_samples = models.IntegerField(
        validators=[
            MinValueValidator(1),    # Minimum value of 1
            MaxValueValidator(23)    # Maximum value of 23
        ],
        help_text="Enter a number between 1 and 23"
        )
    current_number = models.CharField(max_length=20, default='0000000T', editable=False)
    tmp_lot_id = models.CharField(max_length=20, default='TMP0000000000', editable=False)
    project_factory_date_code = models.CharField(max_length=50, default='DEFAULT_CODE', editable=False)
    es_number = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    end_date = models.DateField(null=True, blank=True)
    development = models.FloatField(default='0.0')
    metrology = models.FloatField(default='0.0')
    duplo = models.FloatField(default='0.0')
    other = models.FloatField(default='0.0')
    created_at = models.DateField(null=True, blank=True, auto_now_add=False)
    url = models.CharField(max_length=100,null=True, blank=True)
    # lot_turns = models.IntegerField(default=0)
    # EUV_3300 = models.IntegerField(default=0)
    # EUV_3400 = models.IntegerField(default=0)
    # jpn_ytd = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Lot {self.tmp_lot_id} - {self.status}"

    # def photo_image_tag(self):
    #     if self.photo and self.photo.name:
    #         return mark_safe(f'<img src="{self.photo.name.url}" width="100" height="100" />')
    #     return "No Image"
    # photo_image_tag.short_description = 'Photo Image'


# Remove the separate ActiveForm_Data model and consolidate it into the Lot model with status
class ActiveForm_Data(models.Model):
    wbs = models.ForeignKey(WBS, on_delete=models.CASCADE)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    bu = models.ForeignKey(BU, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)
    requestor = models.ForeignKey(Requestor, on_delete=models.CASCADE)
    # photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    reticle = models.ForeignKey(Reticle, on_delete=models.CASCADE)
    litho = models.ForeignKey(Litho, on_delete=models.CASCADE)
    integrator = models.ForeignKey(Integrator, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    special_focus = models.CharField(max_length=100)
    request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE)
    estimated_end_date = models.DateField()
    no_of_samples = models.IntegerField()
    is_active = models.BooleanField(default=False)
    current_number = models.CharField(max_length=20, default='0000000T', editable=False)
    tmp_lot_id = models.CharField(max_length=20, default='TMP0000000000', editable=False)
    project_factory_date_code = models.CharField(max_length=50, default='DEFAULT_CODE', editable=False)
    es_number = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='Active')
    end_date = models.DateField(null=True, blank=True)
    development = models.FloatField(default='0.0')
    metrology = models.FloatField(default='0.0')
    duplo = models.FloatField(default='0.0')
    other = models.FloatField(default='0.0')
    created_at = models.DateField(null=True, blank=True, auto_now_add=False)
    url = models.CharField(max_length=100,null=True, blank=True)
    # def photo_image_tag(self):
    #     if self.photo and self.photo.name:
    #         return mark_safe(f'<img src="{self.photo.name.url}" width="100" height="100" />')
    #     return "No Image"
    # photo_image_tag.short_description = 'Photo Image'


class CompletedForm_Data(models.Model):
    wbs = models.ForeignKey(WBS, on_delete=models.CASCADE)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    bu = models.ForeignKey(BU, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    project_group = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)
    requestor = models.ForeignKey(Requestor, on_delete=models.CASCADE)
    # photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    reticle = models.ForeignKey(Reticle, on_delete=models.CASCADE)
    litho = models.ForeignKey(Litho, on_delete=models.CASCADE)
    integrator = models.ForeignKey(Integrator, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    special_focus = models.CharField(max_length=100)
    request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE)
    estimated_end_date = models.DateField()
    no_of_samples = models.IntegerField()
    is_active = models.BooleanField(default=False)
    current_number = models.CharField(max_length=20, default='0000000T', editable=False)
    tmp_lot_id = models.CharField(max_length=20, default='TMP0000000000', editable=False)
    project_factory_date_code = models.CharField(max_length=50, default='DEFAULT_CODE', editable=False)
    es_number = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, default='Completed')
    end_date = models.DateField(null=True, blank=True)
    development = models.FloatField(default='0.0')
    metrology = models.FloatField(default='0.0')
    duplo = models.FloatField(default='0.0')
    other = models.FloatField(default='0.0')
    created_at = models.DateField(null=True, blank=True, auto_now_add=False)
    url = models.CharField(max_length=100,null=True, blank=True)
    # def photo_image_tag(self):
    #     if self.photo and self.photo.name:
    #         return mark_safe(f'<img src="{self.photo.name.url}" width="100" height="100" />')
    #     return "No Image"
    # photo_image_tag.short_description = 'Photo Image'


class upload_data(models.Model):
    tmp_lot_id = models.CharField(max_length=255)
    lot_turns = models.FloatField(null=True, blank=True)
    EUV_3300 = models.FloatField(null=True, blank=True)
    EUV_3400 = models.FloatField(null=True, blank=True)
    EXE_5000 = models.FloatField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)  # Changed to IntegerField
    month = models.IntegerField(null=True, blank=True)  # Changed to IntegerField
    jpn_ytd = models.CharField(max_length=255)
    no_of_samples = models.FloatField(null=True, blank=True)  # Added new field

    wbs = models.ForeignKey("WBS", on_delete=models.CASCADE, null=True, blank=True)
    factory = models.ForeignKey("Factory", on_delete=models.CASCADE, null=True, blank=True)
    bu = models.ForeignKey("BU", on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "upload_data"  

    def __str__(self):
        return f"{self.tmp_lot_id} ({self.year}-{self.month})"
    


class BudgetData(models.Model):
    wbs = models.ForeignKey('WBS', on_delete=models.SET_NULL, null=True, blank=True)
    bu = models.ForeignKey('BU', on_delete=models.SET_NULL, null=True, blank=True)
    factory = models.ForeignKey('Factory', on_delete=models.SET_NULL, null=True, blank=True)
    lot_turns_budget = models.FloatField(null=True, blank=True)
    euv3400_budget = models.FloatField(null=True, blank=True)
    exe5000_budget = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.wbs} - {self.bu} - {self.factory}"
    
class LotStatusData(models.Model):
    owner = models.CharField(max_length=255, null=True, blank=True)
    factory = models.CharField(max_length=255, null=True, blank=True)
    lot_id = models.CharField(max_length=255, null=True, blank=True)
    hold_code = models.CharField(max_length=255, null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    current_operation = models.CharField(max_length=255, null=True, blank=True)

    # Storing operation columns dynamically
    oper1 = models.CharField(max_length=255, null=True, blank=True)
    oper2 = models.CharField(max_length=255, null=True, blank=True)
    oper3 = models.CharField(max_length=255, null=True, blank=True)
    oper4 = models.CharField(max_length=255, null=True, blank=True)
    oper5 = models.CharField(max_length=255, null=True, blank=True)
    oper6 = models.CharField(max_length=255, null=True, blank=True)
    oper7 = models.CharField(max_length=255, null=True, blank=True)
    oper8 = models.CharField(max_length=255, null=True, blank=True)
    oper9 = models.CharField(max_length=255, null=True, blank=True)
    oper10 = models.CharField(max_length=255, null=True, blank=True)
    oper11 = models.CharField(max_length=255, null=True, blank=True)
    oper12 = models.CharField(max_length=255, null=True, blank=True)
    oper13 = models.CharField(max_length=255, null=True, blank=True)
    oper14 = models.CharField(max_length=255, null=True, blank=True)
    oper15 = models.CharField(max_length=255, null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.factory} - {self.lot_id}"

class ContractData(models.Model):
    contract = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    lot_turns = models.FloatField(null=True, blank=True)
    euv3400 = models.FloatField(null=True, blank=True)
    exe5000 = models.FloatField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract} ({self.status})"

def upload_to(instance, filename):
    return f"uploads/{instance.folder}/{filename}"

class Folder(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class UploadedFile(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

class UploadRecord(models.Model):
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50)  # Example: 'csv', 'xls'
    uploader = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.file_name} uploaded at {self.uploaded_at}"