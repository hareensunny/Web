from django import forms
from django.contrib import admin
from .models import WBS,ActiveForm_Data, Factory, BU, Department, ProjectGroup, Requestor, Reticle, Integrator, RequestType, Lot, Litho, Location,CompletedForm_Data,upload_data
from import_export.admin import ImportExportModelAdmin

admin.site.register(WBS)
admin.site.register(Factory)
admin.site.register(BU)
admin.site.register(Department)
admin.site.register(ProjectGroup)
admin.site.register(Requestor)
admin.site.register(Litho)
admin.site.register(Location)



admin.site.register(Reticle)
admin.site.register(Integrator)
admin.site.register(RequestType)

class PartialUpdateForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = ['wbs', 'factory', 'bu', 'department', 'project_group', 'requestor', 'is_active', 'status', 'es_number', 'location', 'end_date', 'development', 'metrology', 'duplo', 'other']


class LotAdmin(admin.ModelAdmin):
    list_display = (
        'wbs', 'factory', 'bu', 'department', 'project_group',
        'requestor', 'url', 'reticle', 'integrator', 'topic',
        'special_focus', 'request_type', 'estimated_end_date', 'no_of_samples',
        'is_active', 'litho', 'current_number', 'tmp_lot_id', 'project_factory_date_code'
    )
    search_fields = (
        'wbs__name', 'factory__name', 'bu__name', 'department__name',
        'project_group__name', 'requestor__name', 'url', 'reticle',
        'integrator', 'topic', 'special_focus', 'request_type', 'no_of_samples',
        'is_active', 'current_number', 'tmp_lot_id', 'project_factory_date_code'
    )
    list_filter = (
        'wbs', 'factory', 'bu', 'department', 'project_group', 'requestor',
        'request_type', 'estimated_end_date', 'is_active'
    )

    def save_model(self, request, obj, form, change):
        if change:  # If this is an update
            original_obj = self.model.objects.get(pk=obj.pk)
            for field in form.changed_data:
                setattr(original_obj, field, getattr(obj, field))
            obj = original_obj
        super().save_model(request, obj, form, change)
        if obj.is_active:
            active_data, created = ActiveForm_Data.objects.update_or_create(
                tmp_lot_id=obj.tmp_lot_id,
                defaults={
                    'wbs': obj.wbs,
                    'factory': obj.factory,
                    'bu': obj.bu,
                    'department': obj.department,
                    'project_group': obj.project_group,
                    'requestor': obj.requestor,
                    'url': obj.url,
                    'reticle': obj.reticle,
                    'litho': obj.litho,
                    'integrator': obj.integrator,
                    'topic': obj.topic,
                    'special_focus': obj.special_focus,
                    'request_type': obj.request_type,
                    'estimated_end_date': obj.estimated_end_date,
                    'no_of_samples': obj.no_of_samples,
                    'current_number': obj.current_number,
                    'project_factory_date_code': obj.project_factory_date_code,
                    'es_number': obj.es_number,
                    'location': obj.location,
                    'status': obj.status,
                    'end_date': obj.end_date,
                    'development': obj.development,
                    'metrology': obj.metrology,
                    'duplo': obj.duplo,
                    'other': obj.other,
                    'is_active': obj.is_active
                }
            )
        else:
            ActiveForm_Data.objects.filter(tmp_lot_id=obj.tmp_lot_id).delete()

admin.site.register(Lot, LotAdmin)
# Remove the separate ActiveFormDataAdmin class as the Lot model now handles all statuses
class ActiveFormDataAdmin(admin.ModelAdmin):
    list_display = (
        'wbs', 'factory', 'bu', 'department', 'project_group', 'requestor',
        'url', 'reticle', 'integrator', 'topic', 'special_focus',
        'request_type', 'estimated_end_date', 'no_of_samples', 'is_active', 'location',
        'end_date', 'development', 'metrology', 'duplo', 'other'
    )
    search_fields = (
        'wbs__name', 'factory__name', 'bu__name', 'department__name',
        'project_group__name', 'requestor__name', 'url', 'reticle__name',
        'integrator__name', 'topic', 'special_focus', 'request_type__name',
        'no_of_samples'
    )
    list_filter = (
        'wbs', 'factory', 'bu', 'department', 'project_group', 'requestor',
        'request_type', 'estimated_end_date', 'is_active'
    )
    def save_model(self, request, obj, form, change):
        if change:  # If this is an update
            original_obj = self.model.objects.get(pk=obj.pk)
            for field in form.changed_data:
                setattr(original_obj, field, getattr(obj, field))
            obj = original_obj
        super().save_model(request, obj, form, change)
        if obj.is_active:
            completed_data, created = CompletedForm_Data.objects.update_or_create(
                tmp_lot_id=obj.tmp_lot_id,
                defaults={
                    'wbs': obj.wbs,
                    'factory': obj.factory,
                    'bu': obj.bu,
                    'department': obj.department,
                    'project_group': obj.project_group,
                    'requestor': obj.requestor,
                    'url': obj.url,
                    'reticle': obj.reticle,
                    'litho': obj.litho,
                    'integrator': obj.integrator,
                    'topic': obj.topic,
                    'special_focus': obj.special_focus,
                    'request_type': obj.request_type,
                    'estimated_end_date': obj.estimated_end_date,
                    'no_of_samples': obj.no_of_samples,
                    'current_number': obj.current_number,
                    'project_factory_date_code': obj.project_factory_date_code,
                    'es_number': obj.es_number,
                    'location': obj.location,
                    'status': obj.status,
                    'end_date': obj.end_date,
                    'development': obj.development,
                    'metrology': obj.metrology,
                    'duplo': obj.duplo,
                    'other': obj.other,
                    'is_active': obj.is_active
                }
            )
        else:
            CompletedForm_Data.objects.filter(tmp_lot_id=obj.tmp_lot_id).delete()

admin.site.register(ActiveForm_Data, ActiveFormDataAdmin)

class CompletedFormDataAdmin(admin.ModelAdmin):
    list_display = (
        'wbs', 'factory', 'bu', 'department', 'project_group', 'requestor',
        'url', 'reticle', 'integrator', 'topic', 'special_focus',
        'request_type', 'estimated_end_date', 'no_of_samples', 'is_active', 'location',
        'end_date', 'development', 'metrology', 'duplo', 'other','tmp_lot_id',
    )
    search_fields = (
        'wbs__name', 'factory__name', 'bu__name', 'department__name',
        'project_group__name', 'requestor__name', 'url', 'reticle__name',
        'integrator__name', 'topic', 'special_focus', 'request_type__name',
        'no_of_samples'
    )
    list_filter = (
        'wbs', 'factory', 'bu', 'department', 'project_group', 'requestor',
        'request_type', 'estimated_end_date', 'is_active'
    )
   
admin.site.register(CompletedForm_Data, CompletedFormDataAdmin)

@admin.register(upload_data)
class userdata(ImportExportModelAdmin):
    list_display = (
        'year','tmp_lot_id','EUV_3400','EUV_3300','jpn_ytd','lot_turns','wbs','factory','bu','department'
    )
    list_filter = (
        'year','tmp_lot_id','EUV_3400','EUV_3300','jpn_ytd','lot_turns','wbs','factory','bu','department'
    )