from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .decorators import role_required
from .views import (
    form_view, get_factories, get_bus, get_departments, get_project_groups, get_requestors,
    edit_form_data, waiting_lots, edit_active_form_data, active_form_data_view,
    completed_form_data_view, search_lot, YEAR, JPN_FY, CURRENT_FY,
    department_lot_usage, upload_budget_data, executive_summary_data,
    upload_lot_status_data, lot_status, upload_contract_data, contract_status,
    file_explorer, delete_file, delete_folder, summary_page, presentations, handle_upload
)

urlpatterns = [
    path('auth/login', views.login, name='login'),
    path('auth/callback', views.callback, name='callback'),
    path('auth/logout', views.logout_view, name='logout'),
    path('', views.home, name='home'),

    # AJAX dropdowns
    path('get-factories/', get_factories, name='get_factories'),
    path('get-bus/', get_bus, name='get_bus'),
    path('get-departments/', get_departments, name='get_departments'),
    path('get-project-groups/', get_project_groups, name='get_project_groups'),
    path('get-requestors/', get_requestors, name='get_requestors'),

    # Form and lot views
    path('newlotform/', form_view, name='form_view'),
    path('waiting_lots/', waiting_lots, name='form_data_list'),
    path('active_lots/', active_form_data_view, name='active_form_data_view'),
    path('edit_waiting_lots/<int:pk>/', edit_form_data, name='edit_form_data'),
    path('edit_active_lots/<int:pk>/', edit_active_form_data, name='edit_active_form_data'),
    path('completed_lots/', completed_form_data_view, name='completed_form_data_view'),

    # Search and upload
    path('lot_search/', search_lot, name='search_lot'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('upload_euvdata/', views.upload_euvdata, name='upload_euvdata'),
    path("upload/<str:upload_type>/", handle_upload, name="handle_upload"),

    # Year-based views
    path('year/', YEAR, name="year"),
    path('jpnfy/', JPN_FY, name="jpnfy"),
    path('currentfy/', CURRENT_FY, name="currentfy"),

    # Data usage and summaries (admin/superuser access only)
    path('department-lot-usage/', role_required(['admin', 'superuser'])(department_lot_usage), name='department_lot_usage'),
    path('upload_budget/', role_required(['admin'])(upload_budget_data), name='upload_budget'),
    path('executive_summary/', role_required(['admin', 'superuser'])(executive_summary_data), name='executive_summary'),
    path("summary/", role_required(['admin', 'superuser'])(summary_page), name="summary_page"),
    path("presentations/", role_required(['admin'])(presentations), name="presentations"),

    # Lot and contract status (admin/superuser)
    path("upload-lot-status/", role_required(['admin'])(upload_lot_status_data), name="upload_lot_status"),
    path("lot-status/", role_required(['admin', 'superuser'])(lot_status), name="lot_status"),
    path("upload-contract-data/", role_required(['admin'])(upload_contract_data), name="upload_contract_data"),
    path("contract-status/", role_required(['admin', 'superuser'])(contract_status), name="contract_status"),

    # File management (admin only)
    path('file-explorer/', role_required(['admin'])(file_explorer), name='file_explorer'),
    path('delete/file/<int:file_id>/', role_required(['admin'])(delete_file), name='delete_file'),
    path('delete/folder/<int:folder_id>/', role_required(['admin'])(delete_folder), name='delete_folder'),

    # Data APIs
    path('completed-lots/data/', views.completed_lots_data, name='completed_lots_data'),
    path("completed-lots/factory-counts/", views.completed_factory_counts, name="completed_factory_counts"),
]
