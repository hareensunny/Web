
from urllib import request
import pandas as pd
from django.contrib import messages
import msal
from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse,HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Lot,ActiveForm_Data,CompletedForm_Data, WBS, Factory, BU, Department, ProjectGroup, Requestor, Reticle, Integrator, RequestType, Litho, Location, upload_data,BudgetData,LotStatusData,ContractData,UploadedFile, Folder,UploadRecord
import datetime
from django.core.files.storage import FileSystemStorage
from collections import Counter
from datetime import datetime
from django.db.models.functions import ExtractYear
from django.db.models import Min, Max, Sum, Count, Q
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
import json
from django.contrib.auth import logout
import csv
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
import os
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count

# def role_required(allowed_roles=[]):
#     """
#     Decorator to restrict access to views based on user roles stored in session.
#     """
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#             role = request.session.get('role')  # Get user role from session
#             if role not in allowed_roles:
#                 # Return 403 Forbidden if role not allowed
#                 return HttpResponseForbidden("Access Denied: You do not have permission to view this page.")
#             return view_func(request, *args, **kwargs)  # Call the original view function
#         return _wrapped_view
#     return decorator

# Modify your login callback view to set session['role'] based on Django group
from django.contrib.auth.models import Group


def get_msal_app():
    return msal.ConfidentialClientApplication(
        settings.MICROSOFT_AUTH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MICROSOFT_AUTH_TENANT_ID}",
        client_credential=settings.MICROSOFT_AUTH_CLIENT_SECRET,
    )

def login(request):
    """Redirects user to Microsoft login page."""
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=settings.MICROSOFT_AUTH_REDIRECT_URI
    )
    return HttpResponseRedirect(auth_url)

def callback(request):
    """Handles Microsoft authentication callback and sets user session."""
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Authorization code not provided", status=400)

    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read"],
        redirect_uri=settings.MICROSOFT_AUTH_REDIRECT_URI
    )

    if "error" in result:
        return render(request, "error.html", {"error": result.get("error_description")})

    # Store access token and user info in session
    access_token = result.get("access_token")
    id_token_claims = result.get("id_token_claims")
    user_email = id_token_claims.get("preferred_username")

    request.session["access_token"] = access_token
    request.session["user_info"] = id_token_claims

    print("Trying to authenticate:", user_email)

    try:
        # It's safer to check username if you use email as username
        user = User.objects.get(username=user_email)  # or use .filter(email=user_email).first()

        request.session["user_id"] = user.id

        # Normalize group names and check
        if user.groups.filter(name__iexact='Admin').exists():
            request.session['role'] = 'admin'
        elif user.groups.filter(name__iexact='Superuser').exists():
            request.session['role'] = 'superuser'
        elif user.groups.filter(name__iexact='User').exists():
            request.session['role'] = 'user'
        else:
            return HttpResponse("Email is registered but has no role assigned. Contact Admin.", status=403)

        print("Assigned role:", request.session['role'])
        print("Session Data After Login:", request.session.get("user_info"))

        return redirect("home")

    except User.DoesNotExist:
        return HttpResponse("Your email is not registered with us. Please contact the administrator.", status=403)


def logout_view(request):
    """Logs out the user and redirects to Microsoft logout page."""
    logout(request)  # Django logout
    request.session.flush()  # Clear session data

    azure_logout_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_AUTH_TENANT_ID}/oauth2/v2.0/logout"
    logout_redirect_uri = request.build_absolute_uri('/')

    return redirect(f"{azure_logout_url}?post_logout_redirect_uri={logout_redirect_uri}")

def home(request):
    """Renders the home page with login/logout button based on session."""
    user_info = request.session.get("user_info")

    print("User Info from Session:", user_info)

    return render(request, "pages/home.html", {
        "user_info": user_info
    })

def form_view(request):
    if request.method == 'POST':
        form_data = Lot(
            wbs_id=request.POST['wbs'],
            factory_id=request.POST['factory'],
            bu_id=request.POST['bu'],
            department_id=request.POST['department'],
            project_group_id=request.POST['project_group'],
            requestor_id=request.POST['requestor'],
            # oto=Photo.ophbjects.get(id=request.POST['photo']),
            litho=Litho.objects.get(id=request.POST['litho']),
            reticle=Reticle.objects.get(id=request.POST['reticle']),
            integrator=Integrator.objects.get(id=request.POST['integrator']),
            topic=request.POST['topic'],
            special_focus=request.POST['special_focus'],
            url=request.POST['url'],
            request_type=RequestType.objects.get(id=request.POST['request_type']),
            estimated_end_date=request.POST['estimated_end_date'],
            no_of_samples=request.POST['no_of_samples'],
        )
        form_data.current_number = generate_current_number()
        form_data.tmp_lot_id = generate_tmp_lot_id()
        form_data.project_factory_date_code = generate_project_factory_date_code(request.POST['project_group'], request.POST['factory'])
        form_data.status = 'waiting'
        form_data.save()
        return redirect('form_data_list')

    wbs_list = WBS.objects.all()
    # photo_list = Photo.objects.all()
    litho_list = Litho.objects.all()
    reticle_list = Reticle.objects.all()
    integrator_list = Integrator.objects.all()
    request_type_list = RequestType.objects.all()

    return render(request, 'pages/newlotrequest.html', {
        'wbs_list': wbs_list,
        # 'photo_list': photo_list,
        'litho_list': litho_list,
        'reticle_list': reticle_list,
        'integrator_list': integrator_list,
        'request_type_list': request_type_list,
    })

def waiting_lots(request):
    form_data = Lot.objects.filter(status='waiting')
    raw_factories = (
        Lot.objects.filter(status='waiting')
        .values('factory__name')
        .annotate(count=Count('id'))
        .order_by('factory__name')
    )

    # Convert for template use
    factories = [
        {"name": f["factory__name"], "count": f["count"]}
        for f in raw_factories if f["factory__name"]
    ]

    return render(request, 'pages/waiting_lots.html', {'form_data': form_data,'factories': factories,})

# def active_lots(request):
#     active_form_data = ActiveForm_Data.objects.filter(status='Active')

 

#     return render(request, 'pages/active_lots.html', {
#         'active_form_data': active_form_data
        
#     })

# def completed_lots(request):
#     completed_form_data = CompletedForm_Data.objects.filter(status='Completed')
#     return render(request, 'pages/complete_lots.html', {'completed_form_data': completed_form_data})
def active_lots(request):

    active_form_data = ActiveForm_Data.objects.filter(status='active')
   

    return render(request, 'pages/active_lots.html', {
        'active_form_data': active_form_data,
        
    })

def completed_lots(request):
    completed_form_data = CompletedForm_Data.objects.filter(status__iexact='Completed')

    
    return render(request, 'pages/complete_lots.html', {
        'completed_form_data': completed_form_data
        
    })
def get_factories(request):
    wbs_id = request.GET.get('wbs_id')
    factories = Factory.objects.filter(wbs_id=wbs_id)
    return JsonResponse(list(factories.values('id', 'name')), safe=False)

def get_bus(request):
    factory_id = request.GET.get('factory_id')
    bus = BU.objects.filter(factory_id=factory_id)
    return JsonResponse(list(bus.values('id', 'name')), safe=False)

def get_departments(request):
    bu_id = request.GET.get('bu_id')
    departments = Department.objects.filter(bu_id=bu_id)
    return JsonResponse(list(departments.values('id', 'name')), safe=False)

def get_project_groups(request):
    factory_id = request.GET.get('factory_id')
    project_groups = ProjectGroup.objects.filter(factory_id=factory_id)
    return JsonResponse(list(project_groups.values('id', 'name')), safe=False)

def get_requestors(request):
    factory_id = request.GET.get('factory_id')
    requestors = Requestor.objects.filter(factory_id=factory_id)
    return JsonResponse(list(requestors.values('id', 'name')), safe=False)

def edit_form_data(request, pk):
    form_data = get_object_or_404(Lot, pk=pk)
    
    if request.method == 'POST':
        form_data.wbs_id = request.POST.get('wbs', form_data.wbs_id)
        form_data.factory_id = request.POST.get('factory', form_data.factory_id)
        form_data.bu_id = request.POST.get('bu', form_data.bu_id)
        form_data.department_id = request.POST.get('department', form_data.department_id)
        form_data.project_group_id = request.POST.get('project_group', form_data.project_group_id)
        form_data.requestor_id = request.POST.get('requestor', form_data.requestor_id)
        # form_data.photo_id = request.POST.get('photo', form_data.photo_id)
        form_data.reticle_id = request.POST.get('reticle', form_data.reticle_id)
        form_data.litho_id = request.POST.get('litho', form_data.litho_id)
        form_data.integrator_id = request.POST.get('integrator', form_data.integrator_id)
        form_data.topic = request.POST.get('topic', form_data.topic)
        form_data.special_focus = request.POST.get('special_focus', form_data.special_focus)
        form_data.url = request.POST.get('url', form_data.url)
        form_data.request_type_id = request.POST.get('request_type', form_data.request_type_id)
        form_data.estimated_end_date = request.POST.get('estimated_end_date', form_data.estimated_end_date)
        form_data.no_of_samples = request.POST.get('no_of_samples', form_data.no_of_samples)
        form_data.current_number = form_data.current_number or generate_current_number()
        form_data.tmp_lot_id = request.POST.get('tmp_lot_id', form_data.tmp_lot_id)
        form_data.project_factory_date_code = request.POST.get('project_factory_date_code', form_data.project_factory_date_code)
        form_data.status = request.POST.get('status', form_data.status)
        form_data.es_number = request.POST.get('es_number', form_data.es_number)
        form_data.location_id = request.POST.get('location', form_data.location_id)
        form_data.is_active = 'is_active' in request.POST

        form_data.save()
        if form_data.is_active:
            active_data, created = ActiveForm_Data.objects.update_or_create(
                tmp_lot_id=form_data.tmp_lot_id,
                defaults={
                    'wbs': form_data.wbs,
                    'factory': form_data.factory,
                    'bu': form_data.bu,
                    'department': form_data.department,
                    'project_group': form_data.project_group,
                    'requestor': form_data.requestor,
                    # 'photo': form_data.photo,
                    'reticle': form_data.reticle,
                    'litho': form_data.litho,
                    'integrator': form_data.integrator,
                    'topic': form_data.topic,
                    'special_focus': form_data.special_focus,
                    'url': form_data.url,
                    'request_type': form_data.request_type,
                    'estimated_end_date': form_data.estimated_end_date,
                    'no_of_samples': form_data.no_of_samples,
                    'current_number': form_data.current_number,
                    'project_factory_date_code': form_data.project_factory_date_code,
                    'es_number': form_data.es_number,
                    'location': form_data.location,
                    'status': 'active',
                    'end_date': form_data.end_date,
                    'development': form_data.development,
                    'metrology': form_data.metrology,
                    'duplo': form_data.duplo,
                    'other': form_data.other,
                    'is_active': form_data.is_active
                }
            )
            form_data.delete()
        else:
            # If the form data is not active, remove any associated ActiveForm_Data entries
            ActiveForm_Data.objects.filter(tmp_lot_id=form_data.tmp_lot_id).delete()
        return redirect('active_form_data_view')
    
    return render(request, 'pages/edit_waiting_lots.html', {'form_data': form_data, 'locations': Location.objects.all()})

def active_form_data_view(request):
    active_form_data = ActiveForm_Data.objects.all()

    # Build factory count dictionary
    factory_dict = {}
    for obj in active_form_data:
        if obj.factory:
            name = obj.factory.name
            factory_dict[name] = factory_dict.get(name, 0) + 1

    factories = [{'name': name, 'count': count} for name, count in factory_dict.items()]

    return render(request, 'pages/active_lots.html', {
        'active_form_data': active_form_data,
        'factories': factories,
    })

def generate_current_number():
    current_year =  datetime.now().year
    latest_entry = Lot.objects.filter(current_number__startswith=str(current_year)).order_by('-id').first()
    if latest_entry:
        last_number = int(latest_entry.current_number[len(str(current_year)):-1]) + 1
    else:
        last_number = 0
    return f"{current_year}{str(last_number).zfill(3)}T"

def generate_tmp_lot_id():
    current_year = datetime.now().strftime("%Y%m%d")
    latest_entry = Lot.objects.filter(tmp_lot_id__startswith=f"TMP{current_year}").order_by('-id').first()
    if latest_entry:
        last_number = int(latest_entry.tmp_lot_id[-3:]) + 1
    else:
        last_number = 0
    return f"TMP{current_year}{str(last_number).zfill(3)}"

def generate_project_factory_date_code(project_group, factory):
    current_year = datetime.now().strftime("%Y%m%d")
    project_group_name = ProjectGroup.objects.get(id=project_group).name
    factory_name = Factory.objects.get(id=factory).name
    latest_entry = Lot.objects.filter(project_factory_date_code__startswith=f"{project_group_name}{factory_name}{current_year}").order_by('-id').first()
    if latest_entry:
        last_number = int(latest_entry.project_factory_date_code[-3:]) + 1
    else:
        last_number = 0
    return f"{project_group_name}{factory_name}{current_year}{str(last_number).zfill(3)}"

def edit_active_form_data(request, pk):
    form_data = get_object_or_404(ActiveForm_Data, pk=pk)

    if request.method == 'POST':
        form_data.tmp_lot_id = request.POST.get('tmp_lot_id', form_data.tmp_lot_id)
        form_data.es_number = request.POST.get('es_number', form_data.es_number)
        form_data.location_id = request.POST.get('location', form_data.location_id)
        form_data.end_date = request.POST.get('end_date', form_data.end_date)
        form_data.development = request.POST.get('development', form_data.development)
        form_data.metrology = request.POST.get('metrology', form_data.metrology)
        form_data.duplo = request.POST.get('duplo', form_data.duplo)
        form_data.other = request.POST.get('other', form_data.other)
        form_data.is_active = 'is_active' in request.POST

        form_data.save()

        if form_data.is_active:
            completed_data, created = CompletedForm_Data.objects.update_or_create(
                tmp_lot_id=form_data.tmp_lot_id,
                defaults={
                    'wbs': form_data.wbs,
                    'factory': form_data.factory,
                    'bu': form_data.bu,
                    'department': form_data.department,
                    'project_group': form_data.project_group,
                    'requestor': form_data.requestor,
                    # 'photo': form_data.photo,
                    'reticle': form_data.reticle,
                    'litho': form_data.litho,
                    'integrator': form_data.integrator,
                    'topic': form_data.topic,
                    'special_focus': form_data.special_focus,
                    'url': form_data.url,
                    'request_type': form_data.request_type,
                    'estimated_end_date': form_data.estimated_end_date,
                    'no_of_samples': form_data.no_of_samples,
                    'current_number': form_data.current_number,
                    'project_factory_date_code': form_data.project_factory_date_code,
                    'es_number': form_data.es_number,
                    'location': form_data.location,
                    'status': 'Completed',
                    'end_date': form_data.end_date,
                    'development': form_data.development,
                    'metrology': form_data.metrology,
                    'duplo': form_data.duplo,
                    'other': form_data.other,
                    'is_active': form_data.is_active
                }
            )
            form_data.delete()
            return redirect('completed_form_data_view')
           
        else:
            CompletedForm_Data.objects.filter(tmp_lot_id=form_data.tmp_lot_id).delete()

            return redirect('active_form_data_view')

    return render(request, 'pages/edit_active_lots.html', {'form_data': form_data, 'locations': Location.objects.all()})

def completed_form_data_view(request):
    completed_form_data = CompletedForm_Data.objects.order_by('-id') 

    # Get unique factories
    factories = CompletedForm_Data.objects.values_list('factory__name', flat=True).distinct()

    return render(request, 'pages/complete_lots.html', {
        'completed_form_data': completed_form_data,
        'factories': factories
    })

def completed_factory_counts(request):
    factory_dict = {}
    for obj in CompletedForm_Data.objects.all():
        if obj.factory:
            name = obj.factory.name.strip().upper()
            factory_dict[name] = factory_dict.get(name, 0) + 1

    data = [{"name": name, "count": count} for name, count in factory_dict.items()]
    return JsonResponse(data, safe=False)

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.dateformat import format as date_format

from django.http import JsonResponse
from .models import CompletedForm_Data

def completed_lots_data(request):
    # DataTables parameters
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

    # Factory filter from frontend (optional)
    factory_filter = request.GET.get("factory_filter", "").strip().upper()

    # Base queryset
    queryset = CompletedForm_Data.objects.select_related(
        'factory', 'wbs', 'project_group', 'bu', 'department', 'requestor',
       'reticle', 'litho', 'integrator', 'request_type', 'location'
    ).all()

    # Apply filtering
    if factory_filter:
        queryset = queryset.filter(factory__name__iexact=factory_filter)

    records_total = CompletedForm_Data.objects.count()
    records_filtered = queryset.count()

    # Apply pagination
    paginated_data = queryset[start:start + length]

    # Build DataTables response
    data = []
    for obj in paginated_data:
        data.append({
            "tmp_lot_id": obj.tmp_lot_id,
            "factory": obj.factory.name if obj.factory else "",
            "url": obj.url,
            "wbs": obj.wbs.name if obj.wbs else "",
            "project_group": obj.project_group.name if obj.project_group else "",
            "bu": obj.bu.name if obj.bu else "",
            "department": obj.department.name if obj.department else "",
            "current_number": obj.current_number,
            "requestor": obj.requestor.name if obj.requestor else "",
            "topic": obj.topic,
            "special_focus": obj.special_focus,
            "name": obj.project_factory_date_code,
            "reticle": obj.reticle.name if obj.reticle else "",
            "litho": obj.litho.name if obj.litho else "",
            "integrator": obj.integrator.name if obj.integrator else "",
            "request_type": obj.request_type.name if obj.request_type else "",
            "estimated_end_date": obj.estimated_end_date.strftime("%Y-%m-%d") if obj.estimated_end_date else "",
            "no_of_samples": obj.no_of_samples,
            "es_number": obj.es_number,
            "location": obj.location.name if obj.location else "",
            "status": obj.status,
            "end_date": obj.end_date.strftime("%Y-%m-%d") if obj.end_date else "",
            "development": obj.development,
            "metrology": obj.metrology,
            "duplo": obj.duplo,
            "other": obj.other,
        })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
       "data": data,
    })


from django.http import Http404
from django.shortcuts import render
from .models import Lot, ActiveForm_Data, CompletedForm_Data, upload_data

def search_lot(request):
    combined_data = None
    lot_id = request.GET.get('lot_id')

    if lot_id:
        lot = None
        status = None

        try:
            # Try to find in Lot (waiting)
            lot = Lot.objects.get(tmp_lot_id=lot_id)
            status = 'waiting'
        except Lot.DoesNotExist:
            try:
                # Try to find in ActiveForm_Data (active)
                lot = ActiveForm_Data.objects.get(tmp_lot_id=lot_id)
                status = 'active'
            except ActiveForm_Data.DoesNotExist:
                try:
                    # Try to find in CompletedForm_Data (completed)
                    lot = CompletedForm_Data.objects.get(tmp_lot_id=lot_id)
                    status = 'completed'
                except CompletedForm_Data.DoesNotExist:
                    raise Http404("Lot not found")

        # Fetch Upload Data
        upload_data_info = upload_data.objects.filter(tmp_lot_id=lot_id)

        # Initialize Variables
        years = []
        lot_turns_series = []
        EUV_3400_series = []
        EXE_5000_series = []
        total_lot_turns = 0.0
        total_EUV_3400 = 0.0
        EUV_3300 = None
        jpn_ytd = None
        year = None
        total_flow = 0.0
        TPA = None
        ETA = None
        redline = None
        dict_value = None

        if upload_data_info.exists():
            for item in upload_data_info:
                years.append(int(item.year))
                lot_turns_series.append(float(item.lot_turns))
                EUV_3400_series.append(float(item.EUV_3400))
                EXE_5000_series.append(float(item.EXE_5000))
                total_lot_turns += float(item.lot_turns)
                total_EUV_3400 += float(item.EUV_3400)

            # Static Fields from First Upload Record
            first_item = upload_data_info.first()
            EUV_3300 = first_item.EUV_3300
            jpn_ytd = first_item.jpn_ytd
            year = first_item.year

            # Start and End Dates for TPA, ETA Calculations
            startdate = getattr(lot, 'created_at', None)
            enddate = getattr(lot, 'end_date', None)
            eedate = getattr(lot, 'estimated_end_date', None)

            if startdate and enddate and eedate:
                try:
                    date_diff = enddate - startdate
                    eta_diff = eedate - startdate
                    TPA = date_diff.days
                    ETA = eta_diff.days
                    redline = TPA * 0.9
                    dict_value = ETA / 5
                except Exception:
                    TPA = ETA = redline = dict_value = None

            # Total Flow Calculation (only if lot has fields)
            try:
                total_flow = sum([
                    getattr(lot, 'metrology', 0.0),
                    getattr(lot, 'other', 0.0),
                    getattr(lot, 'duplo', 0.0),
                    getattr(lot, 'development', 0.0),
                ])
            except Exception:
                total_flow = 0.0

        # Combine all data into dictionary
        combined_data = {
            'lot': lot,
            'status': status,
            'tmp_lot_id': lot.tmp_lot_id,
            'total_lot_turns': total_lot_turns,
            'EUV_3300': EUV_3300,
            'total_EUV_3400': total_EUV_3400,
            'jpn_ytd': jpn_ytd,
            'year': year,
            'total_flow': total_flow,
            'years': years,
            'lot_turns_series': lot_turns_series,
            'EUV_3400_series': EUV_3400_series,
            'EXE_5000_series': EXE_5000_series,
            'TPA': TPA,
            'ETA': ETA,
            'redline': redline,
            'dict': dict_value,
        }

        return render(request, 'pages/lotsearch.html', {'combined_data': combined_data})

    # If no lot_id entered yet
    return render(request, 'pages/lotsearch.html')

def dictify(d):
    """Recursively convert defaultdict to a normal dict."""
    if isinstance(d, defaultdict):
        d = {k: dictify(v) for k, v in d.items()}
    return d

def upload_csv(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']

        # Check if it's a valid CSV file
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Please upload a valid CSV file.")

        # Decode the file and handle BOM
        file_data = csv_file.read().decode('utf-8-sig')  # Handles BOM issues-        csv_reader = csv.DictReader(file_data.splitlines())  # Use DictReader for column mapping

        def parse_date(date_str):
            if date_str:
                for fmt in ("%d/%m/%Y", "%Y-%m-%d"):  # Try both formats
                    try:
                        return datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                return None  # If no format matches
            return None

        # Iterate through each row in the CSV
        for row in csv_reader:

            estimated_end_date = parse_date(row.get("estimated_end_date"))
            end_date = parse_date(row.get("end_date"))
            created_at = parse_date(row.get("created_at"))  # Parse 'created_at' from CSV


            # Skip rows with invalid dates
            if not estimated_end_date:
                return HttpResponse(f"Invalid 'estimated_end_date' format in row: {row}")

            # Extract and validate the 'status' column
            status = row.get('status')
            if not status:
                return HttpResponse(f"Missing 'status' field in row: {row}")

            # Extract WBS data
            wbs_name = row.get('wbs')
            if not wbs_name:
                return HttpResponse(f"Missing 'wbs' field in row: {row}")
            wbs, _ = WBS.objects.get_or_create(name=wbs_name)

            # Extract Factory data
            factory_name = row.get('factory')
            if not factory_name:
                return HttpResponse(f"Missing 'factory' field in row: {row}")
            factory, _ = Factory.objects.get_or_create(name=factory_name, wbs=wbs)

            # Extract BU data
            bu_name = row.get('bu')
            if not bu_name:
                return HttpResponse(f"Missing 'bu' field in row: {row}")
            bu, _ = BU.objects.get_or_create(name=bu_name, factory=factory)

            # Extract Department data
            department_name = row.get('department')
            if not department_name:
                return HttpResponse(f"Missing 'department' field in row: {row}")
            department, _ = Department.objects.get_or_create(name=department_name, bu=bu)

            # Extract other fields and related models
            project_group_name = row.get('project_group')
            project_group, _ = ProjectGroup.objects.get_or_create(name=project_group_name, factory=factory)

            requestor_name = row.get('requestor')
            requestor, _ = Requestor.objects.get_or_create(name=requestor_name, factory=factory)

            litho_name = row.get('litho')
            litho, _ = Litho.objects.get_or_create(name=litho_name)

            reticle_name = row.get('reticle')
            reticle, _ = Reticle.objects.get_or_create(name=reticle_name)

            integrator_name = row.get('integrator')
            integrator, _ = Integrator.objects.get_or_create(name=integrator_name)
            request_type_name = row.get('request_type')
            request_type, _ = RequestType.objects.get_or_create(name=request_type_name)

            location_name = row.get('location')
            location, _ = Location.objects.get_or_create(name=location_name)

            tmp_lot_id = row.get("tmp_lot_id")
            if not tmp_lot_id:
                return HttpResponse(f"Missing 'tmp_lot_id' field in row: {row}")

            # Prepare common data
            record_data = {
                "wbs": wbs,
                "factory": factory,
                "bu": bu,
                "department": department,
                "project_group": project_group,
                "requestor": requestor,
                "reticle": reticle,
                "litho": litho,
                "integrator": integrator,
                "topic": row.get("topic"),
                "special_focus": row.get("special_focus"),
                "request_type": request_type,
                "estimated_end_date": estimated_end_date,
                "no_of_samples": row.get("no_of_samples"),
                "current_number": row.get("current_number"),
                "tmp_lot_id": tmp_lot_id,
                "project_factory_date_code": row.get("project_factory_date_code"),
                "es_number": row.get("es_number"),
                "location": location,
                "status": status,
                "end_date": end_date,
                "development": row.get("development", 0),
                "metrology": row.get("metrology", 0),
                "duplo": row.get("duplo", 0),
                "other": row.get("other", 0),
                "url": row.get("url"),
               
            }

            # Check for duplicates and handle them based on the status
            if status.lower() == "completed":
                obj, created = CompletedForm_Data.objects.update_or_create(
                    tmp_lot_id=tmp_lot_id, defaults=record_data
                )
            elif status.lower() == "active":
                obj, created = ActiveForm_Data.objects.update_or_create(
                    tmp_lot_id=tmp_lot_id, defaults=record_data
                )
            else:
                return HttpResponse(f"Invalid 'status' value in row: {row}")
            

            if created:
                obj.created_at = now()  # New record: Set current date
            elif created_at:
                obj.created_at = created_at  # Existing record: Update from CSV
            obj.save()


        return HttpResponse("CSV data has been processed and the models updated successfully.")

    return render(request, 'pages/upload_csv.html')

def upload_euvdata(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']

        # Check if it's a valid CSV file
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Please upload a valid CSV file.")

        # Decode the file and handle BOM
        file_data = csv_file.read().decode('utf-8-sig')
        csv_reader = csv.DictReader(file_data.splitlines())

        for row in csv_reader:
            tmp_lot_id = row.get("Lot ID")
            year_field = row.get("Year")
            wbs_name = row.get("WBS")  # Column for WBS
            factory_name = row.get("Factory")  # Column for Factory
            bu_name = row.get("BU")  # Column for BU
            department_name = row.get("Dpmt")  # Column for Department
            no_of_samples = row.get("no_of_samples")  # Added for no_of_samples

            if not tmp_lot_id or not year_field:
                print(f"Skipping row with missing data: {row}")
                continue

            try:
                date_obj = datetime.strptime(year_field, "%Y-%m-%d")
                year = date_obj.year
                month = date_obj.month
            except ValueError:
                print(f"Invalid date format in 'Year' field: {row}")
                continue

            try:
                no_of_samples = float(no_of_samples) if no_of_samples else None
            except ValueError:
                print(f"Invalid 'No of Samples' value: {no_of_samples}")
                no_of_samples = None

            # Fetch related objects safely
            wbs_obj = WBS.objects.filter(name=wbs_name).first() if wbs_name else None
            factory_obj = Factory.objects.filter(name=factory_name).first() if factory_name else None
            bu_obj = BU.objects.filter(name=bu_name).first() if bu_name else None
            department_obj = Department.objects.filter(name=department_name).first() if department_name else None

            record_data = {
                "tmp_lot_id": tmp_lot_id,
                "lot_turns": row.get("Total_Lots"),
                "EUV_3300": row.get("3300_EUV"),
                "EUV_3400": row.get("3400_EUV"),
                "EXE_5000":row.get("EXE_5000"),
                "year": year,
                "month": month,
                "jpn_ytd": row.get("JPN_YTD"),
                "wbs": wbs_obj,
                "factory": factory_obj,
                "bu": bu_obj,
                "no_of_samples": no_of_samples,  # Include no_of_samples
                "department": department_obj,
            }

            obj, created = upload_data.objects.update_or_create(
                tmp_lot_id=tmp_lot_id, year=year, month=month, defaults=record_data
            )

        return HttpResponse("CSV data has been processed successfully.")

    return render(request, 'pages/upload_euvdata.html')

def upload_budget_data(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']

        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Please upload a valid CSV file.")

        # Decode file and handle BOM
        file_data = csv_file.read().decode('utf-8-sig')
        csv_reader = csv.DictReader(file_data.splitlines())

        for row in csv_reader:
            wbs_name = row.get("WBS")
            bu_name = row.get("BU")
            factory_name = row.get("Factory")
            lot_turns_budget = row.get("Total Lotturns Budget")
            euv3400_budget = row.get("Total EUV3400 Budget")
            exe5000_budget = row.get("Total EXE5000 Budget")

            try:
                lot_turns_budget = float(lot_turns_budget) if lot_turns_budget else None
                euv3400_budget = float(euv3400_budget) if euv3400_budget else None
                exe5000_budget = float(exe5000_budget) if exe5000_budget else None
            except ValueError:
                print(f"Invalid numerical value in row: {row}")
                continue

            # Fetch related objects
            wbs_obj = WBS.objects.filter(name=wbs_name).first() if wbs_name else None
            bu_obj = BU.objects.filter(name=bu_name).first() if bu_name else None
            factory_obj = Factory.objects.filter(name=factory_name).first() if factory_name else None

            record_data = {
                "wbs": wbs_obj,
                "bu": bu_obj,
                "factory": factory_obj,
                "lot_turns_budget": lot_turns_budget,
                "euv3400_budget": euv3400_budget,
                "exe5000_budget": exe5000_budget,
            }

            obj, created = BudgetData.objects.update_or_create(
                wbs=wbs_obj, bu=bu_obj, factory=factory_obj, defaults=record_data
            )

        return HttpResponse("CSV data has been processed successfully.")
    
    return render(request, 'pages/upload_budget_data.html')

def upload_lot_status_data(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']

        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Please upload a valid CSV file.")

        # Decode file and handle BOM
        file_data = csv_file.read().decode('utf-8-sig')
        csv_reader = csv.DictReader(file_data.splitlines())

        for row in csv_reader:
            try:
                # Create a new record
                LotStatusData.objects.create(
                    owner=row.get("Owner"),
                    factory=row.get("Factory"),
                    lot_id=row.get("Lot id"),
                    hold_code=row.get("Holdcode"),
                    priority=int(row.get("Prio")) if row.get("Prio") else None,
                    current_operation=row.get("Current_Operation"),
                   oper1=row.get("Oper1"),
                    oper2=row.get("Oper2"),
                    oper3=row.get("Oper3"),
                        oper4=row.get("Oper4"),
                    oper5=row.get("Oper5"),
                    oper6=row.get("Oper6"),
                    oper7=row.get("Oper7"),
                    oper8=row.get("Oper8"),
                    oper9=row.get("Oper9"),
                    oper10=row.get("Oper10"),
                    oper11=row.get("Oper11"),
                    oper12=row.get("Oper12"),
                    oper13=row.get("Oper13"),
                    oper14=row.get("Oper14"),
                    oper15=row.get("Oper15"),
                )
            except ValueError:
                print(f"Invalid data in row: {row}")
                continue

        return HttpResponse("CSV data for Lot Status has been uploaded successfully.")

    return render(request, 'pages/upload_lotstatus_data.html')

def upload_contract_data(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']

        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Please upload a valid CSV file.")

        # Decode file and handle BOM
        file_data = csv_file.read().decode('utf-8-sig')
        csv_reader = csv.DictReader(file_data.splitlines())

        for row in csv_reader:
            try:
                effective_date = datetime.strptime(row.get("Effective Date", ""), "%d/%m/%Y").date() if row.get("Effective Date") else None
                termination_date = datetime.strptime(row.get("Termination Date", ""), "%d/%m/%Y").date() if row.get("Termination Date") else None
                lot_turns = float(row.get("Lot Turns", 0)) if row.get("Lot Turns") else 0.0
                euv3400 = float(row.get("EUV3400", 0)) if row.get("EUV3400") else 0.0
                exe5000 = float(row.get("EXE5000", 0)) if row.get("EXE5000") else 0.0

                # Create or update contract data
                ContractData.objects.update_or_create(
                    contract=row.get("Contract"),
                    defaults={
                        "status": row.get("Status"),
                        "effective_date": effective_date,
                        "termination_date": termination_date,
                        "lot_turns": lot_turns,
                        "euv3400": euv3400,
                        "exe5000": exe5000,
                    }
                )
            except ValueError:
                print(f"Invalid data in row: {row}")
                continue

        return HttpResponse("CSV data for Contract Data has been uploaded successfully.")

    return render(request, 'pages/upload_contract_data.html')

from collections import defaultdict
from django.db.models import Sum

def calculate_lot_turns_by_factory_bu_wbs(selected_wbs=None, selected_years=None):
    """
    Aggregates the total lot_turns for each Factory, BU, and WBS, and filters by selected WBS and years.
    """
    query = upload_data.objects.all()

    # Apply filters
    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)
    if selected_years:
        query = query.filter(year__in=selected_years)

    # Aggregate lot_turns by Factory, BU, and WBS
    aggregated_data = query.values('factory__name', 'bu__name', 'wbs__name').annotate(
        total_lot_turns=Sum('lot_turns')
    ).order_by('factory__name', 'bu__name', 'wbs__name')

    # Structure data for the chart
    chart_data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for row in aggregated_data:
        factory_name = row['factory__name'] or "Unknown Factory"
        bu_name = row['bu__name'] or "Unknown BU"
        wbs_name = row['wbs__name'] or "Unknown WBS"
        lot_turns = row['total_lot_turns'] or 0  # Handle null values with 0

        chart_data[factory_name][bu_name][wbs_name] = lot_turns  # Fixed indentation

    return chart_data


def calculate_exe500_by_factory_bu_wbs(selected_wbs=None, selected_years=None):
    """
    Aggregates the total lot_turns for each Factory, BU, and WBS, and filters by selected WBS and years.
    """
    query = upload_data.objects.all()

    # Apply filters
    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)
    if selected_years:
        query = query.filter(year__in=selected_years)

    # Aggregate EUV_3400 by Factory, BU, and WBS
    aggregated_data = query.values('factory__name', 'bu__name', 'wbs__name').annotate(
        total_EXE_5000=Sum('EXE_5000')
    ).order_by('factory__name', 'bu__name', 'wbs__name')

    # Structure data for the chart
    chart_data1 = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for row in aggregated_data:
        factory_name = row['factory__name'] or "Unknown Factory"
        bu_name = row['bu__name'] or "Unknown BU"
        wbs_name = row['wbs__name'] or "Unknown WBS"
        EXE_5000 = row['total_EXE_5000'] or 0  # Handle null values with 0


        chart_data1[factory_name][bu_name][wbs_name] = EXE_5000

    return chart_data1

def calculate_EUV_3400_by_factory_bu_wbs(selected_wbs=None, selected_years=None):
    """
    Aggregates the total EUV_3400 for each Factory, BU, and WBS, and filters by selected WBS and years.
    """
    query = upload_data.objects.all()

    # Apply filters
    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)
    if selected_years:
        query = query.filter(year__in=selected_years)

    # Aggregate EUV_3400 by Factory, BU, and WBS
    aggregated_data = query.values('factory__name', 'bu__name', 'wbs__name').annotate(
        total_EUV_3400=Sum('EUV_3400')
    ).order_by('factory__name', 'bu__name', 'wbs__name')

    # Structure data for the chart
    chart1_data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for row in aggregated_data:
        factory_name = row['factory__name'] or "Unknown Factory"
        bu_name = row['bu__name'] or "Unknown BU"
        wbs_name = row['wbs__name'] or "Unknown WBS"
        EUV_3400 = round(row['total_EUV_3400'] or 0, 2)

        chart1_data[factory_name][bu_name][wbs_name] = EUV_3400

    return chart1_data

def calculate_cumulative_EUV_3400(selected_wbs, selected_years):
    """
    Calculates the cumulative EUV_3400 used for each month across the selected years.
    """
    cumulative_data = defaultdict(float)
    cumulative_sum = 0

    # Fetch the filtered data
    query = upload_data.objects.filter(
        wbs__name=selected_wbs,
        year__in=selected_years
    ).order_by('year', 'month')

    # Loop through the data and calculate cumulative sum
    for entry in query:
        month_year =  f"{entry.year}-{str(entry.month).zfill(2)}"   # Format month-year as YYYY-MM
        cumulative_sum += entry.EUV_3400 or 0  # Add EUV_3400 to cumulative sum
        cumulative_data[month_year] = round(cumulative_sum, 2)  # Round to 2 decimals

    # Ensure all months are included in the selected years
    months = list(cumulative_data.keys())
    cumulative_values = list(cumulative_data.values())

    return months, cumulative_values

def calculate_cumulative_no_of_samples(selected_wbs, selected_years):
    """
    Calculates the cumulative no_of_samples used for each month across the selected years.
    """
    cumulative_data = defaultdict(float)
    cumulative_sum = 0

    # Fetch the filtered data
    query = upload_data.objects.filter(
        wbs__name=selected_wbs,
        year__in=selected_years
    ).order_by('year', 'month')

    # Loop through the data and calculate cumulative sum
    for entry in query:
        month_year =  f"{entry.year}-{str(entry.month).zfill(2)}"   # Format month-year as YYYY-MM
        cumulative_sum += entry.no_of_samples or 0  # Add no_of_samples to cumulative sum
        cumulative_data[month_year] = round(cumulative_sum, 2)  # Round to 2 decimals

    # Ensure all months are included in the selected years
    months = list(cumulative_data.keys())
    cumulative_values = list(cumulative_data.values())

    return months, cumulative_values

def calculate_cumulative_lot_turns(selected_wbs, selected_years):
    """
    Calculates cumulative lot turns for each month across selected years.
    """
    # Initialize cumulative data
    cumulative_data = defaultdict(float)
    cumulative_sum = 0

    # Fetch lot data filtered by WBS and years
    query = upload_data.objects.filter(wbs__name=selected_wbs, year__in=selected_years).order_by('year', 'month')

    # Iterate through query results to calculate cumulative values
    for entry in query:
        month_year = f"{entry.year}-{str(entry.month).zfill(2)}"  # Format as YYYY-MM
        cumulative_sum += entry.lot_turns or 0  # Add lot_turns to cumulative sum
        cumulative_data[month_year] = round(cumulative_sum, 2)  # Round to 2 decimals

    # Extract months and values for the graph
    months = list(cumulative_data.keys())
    cumulative_values = list(cumulative_data.values())

    return months, cumulative_values

def calculate_cumulative_exe500(selected_wbs, selected_years):
    """
    Calculates cumulative lot turns for each month across selected years.
    """
    # Initialize cumulative data
    cumulative_data = defaultdict(float)
    cumulative_sum = 0

    # Fetch lot data filtered by WBS and years
    query = upload_data.objects.filter(wbs__name=selected_wbs, year__in=selected_years).order_by('year', 'month')

    # Iterate through query results to calculate cumulative values
    for entry in query:
        month_year = f"{entry.year}-{str(entry.month).zfill(2)}"  # Format as YYYY-MM
        cumulative_sum += entry.EXE_5000 or 0  # Add lot_turns to cumulative sum
        cumulative_data[month_year] = round(cumulative_sum, 2)  # Round to 2 decimals

    # Extract months and values for the graph
    months = list(cumulative_data.keys())
    cumulative_values = list(cumulative_data.values())

    return months, cumulative_values


def calculate_EUV3400_per_wbs_and_year(selected_wbs=None, selected_years=None):
    """
    Calculates the total EUV_3400 for each WBS and year.
    """
    query = upload_data.objects.all()

    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)

    if selected_years:
        query = query.filter(year__in=selected_years)

    aggregated_data2 = query.values('year', 'wbs__name').annotate(
        total_EUV_3400=Sum('EUV_3400')
    ).order_by('year', 'wbs__name')

    EUV_3400_by_wbs_and_year = defaultdict(lambda: defaultdict(float))
    year_totals2 = defaultdict(float)
    wbs_totals2 = defaultdict(float)
    grand_total2 = 0

    for row in aggregated_data2:
        year = row['year']
        wbs_name = row['wbs__name']
        EUV_3400 = row['total_EUV_3400']
        EUV_3400_by_wbs_and_year[year][wbs_name] += EUV_3400
        year_totals2[year] += EUV_3400
        wbs_totals2[wbs_name] += EUV_3400
        grand_total2 += EUV_3400

    return EUV_3400_by_wbs_and_year, year_totals2, wbs_totals2, grand_total2

def calculate_no_of_samples_per_wbs_and_year(selected_wbs=None, selected_years=None):
    """
    Calculates the total no_of_samples for each WBS and year.
    """
    query = upload_data.objects.all()

    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)

    if selected_years:
        query = query.filter(year__in=selected_years)

    aggregated_data1 = query.values('year', 'wbs__name').annotate(
        total_no_of_samples=Sum('no_of_samples')
    ).order_by('year', 'wbs__name')

    no_of_samples_by_wbs_and_year = defaultdict(lambda: defaultdict(float))
    year_totals1 = defaultdict(float)
    wbs_totals1 = defaultdict(float)
    grand_total1 = 0

    for row in aggregated_data1:
        year = row['year']
        wbs_name = row['wbs__name']
        no_of_samples = row['total_no_of_samples']
        no_of_samples_by_wbs_and_year[year][wbs_name] += no_of_samples
        year_totals1[year] += no_of_samples
        wbs_totals1[wbs_name] += no_of_samples
        grand_total1 += no_of_samples

    return no_of_samples_by_wbs_and_year, year_totals1, wbs_totals1, grand_total1

def calculate_lot_turns_per_wbs_and_year(selected_wbs=None, selected_years=None):
    """
    Calculates the total lot_turns for each WBS and year.
    """
    query = upload_data.objects.all()

    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)

    if selected_years:
        query = query.filter(year__in=selected_years)

    aggregated_data = query.values('year', 'wbs__name').annotate(total_lot_turns=Sum('lot_turns')).order_by('year', 'wbs__name')

    lot_turns_by_wbs_and_year = defaultdict(lambda: defaultdict(float))
    year_totals = defaultdict(float)
    wbs_totals = defaultdict(float)
    grand_total = 0

    for row in aggregated_data:
        year = row['year']
        wbs_name = row['wbs__name']
        lot_turns = row['total_lot_turns']
        lot_turns_by_wbs_and_year[year][wbs_name] += lot_turns
        year_totals[year] += lot_turns
        wbs_totals[wbs_name] += lot_turns
        grand_total += lot_turns

    return lot_turns_by_wbs_and_year, year_totals, wbs_totals, grand_total

def calculate_exe500_per_wbs_and_year(selected_wbs=None, selected_years=None):
    
    query = upload_data.objects.all()

    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)

    if selected_years:
        query = query.filter(year__in=selected_years)

    aggregated_data3 = query.values('year', 'wbs__name').annotate(
        total_EXE_5000=Sum('EXE_5000')
    ).order_by('year', 'wbs__name')

    EXE_5000_by_wbs_and_year = defaultdict(lambda: defaultdict(float))
    year_totals3 = defaultdict(float)
    wbs_totals3 = defaultdict(float)
    grand_total3 = 0

    for row in aggregated_data3:
        year = row['year']
        wbs_name = row['wbs__name']
        EXE_5000 = row['total_EXE_5000'] or 0
        EXE_5000_by_wbs_and_year[year][wbs_name] += EXE_5000
        year_totals3[year] += EXE_5000
        wbs_totals3[wbs_name] += EXE_5000
        grand_total3 += EXE_5000

    return EXE_5000_by_wbs_and_year, year_totals3, wbs_totals3, grand_total3

def get_unique_years_and_wbs():
    """
    Retrieves unique years and WBS from the upload_data model.
    """
    unique_years = upload_data.objects.values('year').distinct().order_by('year')
    unique_wbs = upload_data.objects.values_list('wbs__name', flat=True).distinct().order_by('wbs__name')
    
    return unique_years, unique_wbs
def get_unique_wbs_and_jpnfy():
    """
    Retrieves unique WBS and JPN_YTD values from the upload_data model.
    """
    unique_wbs = upload_data.objects.values_list('wbs__name', flat=True).distinct().order_by('wbs__name')
    unique_jpnfy = upload_data.objects.values_list('jpn_ytd', flat=True).distinct().order_by('jpn_ytd')

    return unique_wbs, unique_jpnfy
import calendar

def YEAR(request):
    """
    View to display and filter data by year and WBS.
    """
    unique_years, unique_wbs = get_unique_years_and_wbs()
    default_wbs = 'BU' if 'BU' in unique_wbs else (unique_wbs[0] if unique_wbs else '')
    selected_wbs_chart = request.GET.get('chart_wbs_name', default_wbs)
    selected_years_chart = request.GET.get('chart_years', None)

    if not selected_years_chart and unique_years:
        selected_years_chart = str(unique_years.order_by('year').last()['year'])

    selected_years_chart = [selected_years_chart]
    selected_wbs_table = request.GET.get('table_wbs_name', '')
    selected_years_table = request.GET.get('table_years', None)

    months, cumulative_data, cumulative_data1, cumulative_data2, cumulative_data3 = [], [], [], [], []

    if selected_years_chart and selected_wbs_chart:
        months_full, cumulative_data = calculate_cumulative_lot_turns(selected_wbs_chart, selected_years_chart)
        cumulative_data1 = calculate_cumulative_no_of_samples(selected_wbs_chart, selected_years_chart)
        cumulative_data2 = calculate_cumulative_EUV_3400(selected_wbs_chart, selected_years_chart)
        cumulative_data3 = calculate_cumulative_exe500(selected_wbs_chart, selected_years_chart)

        formatted_months = [calendar.month_abbr[int(m.split("-")[1])] for m in months_full]

    def get_first_value(data):
        """
        Extracts the first numeric value from cumulative data.
        Handles cases where the data is a tuple with (months, values).
        """
        if isinstance(data, tuple) and len(data) == 2 and isinstance(data[1], list):  
            return float(data[1][0]) if data[1] else 0
        if isinstance(data, list) and data:  
            if isinstance(data[0], (int, float)):  
                return float(data[0])
            elif isinstance(data[0], list) and data[0]:  
                return float(data[0][0])
            elif isinstance(data[0], dict) and 'value' in data[0]:  
                return float(data[0]['value'])
        return 0  

    def calculate_blue_line_values(cumulative_data):
        first_month_value = get_first_value(cumulative_data)
        if first_month_value == 0:
            first_month_value = 1

        ffvalue = (first_month_value * 12)
        blue_value = ((first_month_value * 12) + (0.20 * ffvalue)) / 12

        blue_line_values = [blue_value]
        for _ in range(11):  
            blue_line_values.append(blue_line_values[-1] + blue_value)

        return blue_line_values[:12]  

    blue_line_values = calculate_blue_line_values(cumulative_data)
    blue_line_values1 = calculate_blue_line_values(cumulative_data1)
    blue_line_values2 = calculate_blue_line_values(cumulative_data2)
    blue_line_values3 = calculate_blue_line_values(cumulative_data3)

    # Prepare table data for exe500
    EXE_5000_by_wbs_and_year, year_totals3, wbs_totals3, grand_total3 = calculate_exe500_per_wbs_and_year(
        selected_wbs_table if selected_wbs_table else None,
        selected_years_table if selected_years_table else None
    )
     # Prepare table data
    lot_turns_by_wbs_and_year, year_totals, wbs_totals, grand_total = calculate_lot_turns_per_wbs_and_year(
        selected_wbs_table if selected_wbs_table else None,
        selected_years_table if selected_years_table else None
    )

    no_of_samples_by_wbs_and_year, year_totals1, wbs_totals1, grand_total1 = calculate_no_of_samples_per_wbs_and_year(
        selected_wbs_table if selected_wbs_table else None,
        selected_years_table if selected_years_table else None
    )

    EUV_3400_by_wbs_and_year, year_totals2, wbs_totals2, grand_total2 = calculate_EUV3400_per_wbs_and_year(
        selected_wbs_table if selected_wbs_table else None,
        selected_years_table if selected_years_table else None
    )

    # Aggregate data for charts
    chart_data = calculate_lot_turns_by_factory_bu_wbs(selected_wbs_chart, selected_years_chart)
    chart1_data = calculate_EUV_3400_by_factory_bu_wbs(selected_wbs_chart, selected_years_chart)
    chart_data1 = calculate_exe500_by_factory_bu_wbs(selected_wbs_chart, selected_years_chart)
    

    chart_data = dictify(chart_data)
    chart1_data = dictify(chart1_data)
    chart_data1 = dictify(chart_data1)

    context = {
        'unique_years': unique_years,
        'unique_wbs': unique_wbs,

        'blue_line_values': json.dumps(blue_line_values),
        'blue_line_values1': json.dumps(blue_line_values1),
        'blue_line_values2': json.dumps(blue_line_values2),
        'blue_line_values3': json.dumps(blue_line_values3),

        'selected_wbs_chart': selected_wbs_chart,
        'selected_years_chart': selected_years_chart,

        'selected_wbs_table': selected_wbs_table,
        'selected_years_table': selected_years_table,

        'lot_turns_by_wbs_and_year': lot_turns_by_wbs_and_year,
        'no_of_samples_by_wbs_and_year': no_of_samples_by_wbs_and_year,
        'EUV_3400_by_wbs_and_year': EUV_3400_by_wbs_and_year,
        'EXE_5000_by_wbs_and_year':EXE_5000_by_wbs_and_year,  

        'year_totals': year_totals,
        'wbs_totals': wbs_totals,
        'grand_total': grand_total,

        'year_totals1': year_totals1,
        'wbs_totals1': wbs_totals1,
        'grand_total1': grand_total1,

        'year_totals2': year_totals2,
        'wbs_totals2': wbs_totals2,
        'grand_total2': grand_total2,

        'year_totals3': year_totals3,  
        'wbs_totals3': wbs_totals3,  
        'grand_total3': grand_total3,  

        'months': json.dumps(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]),  
        'cumulative_data': cumulative_data,
        'cumulative_data1': cumulative_data1,
        'cumulative_data2': cumulative_data2,
        'cumulative_data3': cumulative_data3,

        'chart_data': json.dumps(chart_data),
        'chart1_data': json.dumps(chart1_data),
        'chart_data1': json.dumps(chart_data1),  
    }

    return render(request, 'pages/year.html', context)
def JPN_FY(request):
    unique_wbs = upload_data.objects.values_list('wbs__name', flat=True).distinct().order_by('wbs__name')
    unique_jpnfy = upload_data.objects.values_list('jpn_ytd', flat=True).distinct().order_by('-jpn_ytd')

    selected_wbs = request.GET.get('chart_wbs_name', unique_wbs[0] if unique_wbs else '')
    selected_jpnfy = request.GET.get('chart_jpnfy')

    if not selected_jpnfy and unique_jpnfy.exists():
        selected_jpnfy = str(unique_jpnfy.first())

    query = upload_data.objects.all()
    if selected_wbs:
        query = query.filter(wbs__name=selected_wbs)
    if selected_jpnfy:
        query = query.filter(jpn_ytd=selected_jpnfy)

    monthly_data1 = query.values('year', 'month').annotate(
        total_lot_turns=Sum('lot_turns')).order_by('year', 'month')

    monthly_data = query.values('year', 'month', 'factory__name').annotate(
        total_lot_turns=Sum('lot_turns')
    ).order_by('year', 'month', 'factory__name')

    aggregated_data = query.values('factory__name', 'bu__name').annotate(
        total_lot_turns=Sum('lot_turns')
    ).order_by('factory__name', 'bu__name')

    chart_data = {}
    for row in aggregated_data:
        factory = row['factory__name']
        bu = row['bu__name']
        lot_turns = round(row['total_lot_turns'], 2)

        if factory not in chart_data:
            chart_data[factory] = {}
        chart_data[factory][bu] = lot_turns

    chart_data1 = {}
    for row in monthly_data:
        month = f"{row['month']}/{row['year']}"
        factory = row['factory__name']
        lot_turns = round(row['total_lot_turns'], 2)

        if month not in chart_data1:
            chart_data1[month] = {}
        chart_data1[month][factory] = lot_turns

    table_data = {}
    for row in aggregated_data:
        factory_name = row['factory__name']
        bu_name = row['bu__name']
        lot_turns = round(row['total_lot_turns'], 2)

        if factory_name not in table_data:
            table_data[factory_name] = {'total_factory_lot_turns': 0, 'bus': {}}

        table_data[factory_name]['total_factory_lot_turns'] += lot_turns
        table_data[factory_name]['bus'][bu_name] = lot_turns

    total_lot_turns = round(query.aggregate(total_lot_turns=Sum('lot_turns'))['total_lot_turns'] or 0, 2)

    table_data1 = []
    grand_total = 0
    seen_months = set()
    for row in monthly_data1:
        month_name = f"{row['month']}/{row['year']}"
        total_lot_turns1 = round(row['total_lot_turns'], 2)
        grand_total += total_lot_turns1
        if month_name not in seen_months:
            table_data1.append({
                'month': month_name,
                'total_lot_turns': total_lot_turns1,
                'factories': []
            })
            seen_months.add(month_name)

    context = {
        'unique_wbs': unique_wbs,
        'unique_jpnfy': unique_jpnfy,
        'selected_wbs_chart': selected_wbs,
        'selected_jpnfy_chart': selected_jpnfy,
        'table_data': table_data,
        'total_lot_turns': total_lot_turns,
        'chart_data': json.dumps(chart_data),
        'table_data1': table_data1,
        'chart_data1': json.dumps(chart_data1),
    }

    return render(request, 'pages/jpnfy.html', context)
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Q
import json
from django.template.loader import render_to_string
from .models import upload_data, BudgetData, WBS

def CURRENT_FY(request):
    # STEP 1: Always load full list of Factory-BU
    all_factory_bu = (
        upload_data.objects.values_list("factory__name", "bu__name")
        .distinct()
        .order_by("factory__name", "bu__name")
    )
    factory_bu_choices = [f"{f} - {b}" for f, b in all_factory_bu if f and b]

    # STEP 2: Get selected factory-bu from request
    selected_factory_bu = request.GET.get("factory_bu")

    # STEP 3: Get unique JPN fiscal years
    unique_jpnfy = list(
        upload_data.objects.values_list("jpn_ytd", flat=True)
        .distinct()
        .order_by("jpn_ytd")
    )
    highest_jpnfy = unique_jpnfy[-1] if unique_jpnfy else None

    # STEP 4: Base query - current FY data
    base_query = upload_data.objects.filter(jpn_ytd=highest_jpnfy)

    # STEP 5: Apply filter if factory_bu selected
    if selected_factory_bu:
        try:
            factory, bu = selected_factory_bu.split(" - ")
            base_query = base_query.filter(factory__name=factory, bu__name=bu)
        except ValueError:
            pass

    # STEP 6: Prepare WBS summary data
    summary_data = {
        "lot_turns": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
        "EUV_3400": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
        "EXE_5000": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
    }

    wbs_list = WBS.objects.all().order_by("name")

    for wbs in wbs_list:
        fb_queryset = upload_data.objects.filter(wbs=wbs).values("factory__name", "bu__name").distinct()
        for fb in fb_queryset:
            factory_bu = f"{fb['factory__name']} - {fb['bu__name']}"
            if selected_factory_bu and factory_bu != selected_factory_bu:
                continue

            # Lot Turns
            lt_budget = BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).aggregate(total_budget=Sum("lot_turns_budget"))["total_budget"] or 0
            lt_consumed_qs = upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).values("jpn_ytd").annotate(consumed=Sum("lot_turns"))
            lt_consumed_by_year = {x["jpn_ytd"]: round(x["consumed"], 2) for x in lt_consumed_qs}
            lt_total = sum(lt_consumed_by_year.values())
            lt_remaining = round(lt_budget - lt_total, 2)

            summary_data["lot_turns"][wbs.name]["budget"] += lt_budget
            summary_data["lot_turns"][wbs.name]["consumed"] += lt_total
            summary_data["lot_turns"][wbs.name]["remaining"] += lt_remaining
            for year, value in lt_consumed_by_year.items():
                summary_data["lot_turns"][wbs.name]["consumed_by_year"][year] += value
            summary_data["lot_turns"][wbs.name]["table_data"].append({
                "order_segment": factory_bu,
                "total_budget": round(lt_budget, 2),
                "years_data": lt_consumed_by_year,
                "consumed": lt_total,
                "remaining": lt_remaining,
            })

            # EUV_3400
            euv_budget = BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).aggregate(total_budget=Sum("euv3400_budget"))["total_budget"] or 0
            euv_qs = upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).values("jpn_ytd").annotate(consumed=Sum("EUV_3400"))
            euv_by_year = {x["jpn_ytd"]: round(x["consumed"], 2) for x in euv_qs}
            euv_total = sum(euv_by_year.values())
            euv_remaining = round(euv_budget - euv_total, 2)

            summary_data["EUV_3400"][wbs.name]["budget"] += euv_budget
            summary_data["EUV_3400"][wbs.name]["consumed"] += euv_total
            summary_data["EUV_3400"][wbs.name]["remaining"] += euv_remaining
            for year, value in euv_by_year.items():
                summary_data["EUV_3400"][wbs.name]["consumed_by_year"][year] += value
            summary_data["EUV_3400"][wbs.name]["table_data"].append({
                "order_segment": factory_bu,
                "total_budget": round(euv_budget, 2),
                "years_data": euv_by_year,
                "consumed": euv_total,
                "remaining": euv_remaining,
            })

            # EXE_5000
            exe_budget = BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).aggregate(total_budget=Sum("exe5000_budget"))["total_budget"] or 0
            exe_qs = upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).values("jpn_ytd").annotate(consumed=Sum("EXE_5000"))
            exe_by_year = {x["jpn_ytd"]: round(x["consumed"], 2) for x in exe_qs}
            exe_total = sum(exe_by_year.values())
            exe_remaining = round(exe_budget - exe_total, 2)

            summary_data["EXE_5000"][wbs.name]["budget"] += exe_budget
            summary_data["EXE_5000"][wbs.name]["consumed"] += exe_total
            summary_data["EXE_5000"][wbs.name]["remaining"] += exe_remaining
            for year, value in exe_by_year.items():
                summary_data["EXE_5000"][wbs.name]["consumed_by_year"][year] += value
            summary_data["EXE_5000"][wbs.name]["table_data"].append({
                "order_segment": factory_bu,
                "total_budget": round(exe_budget, 2),
                "years_data": exe_by_year,
                "consumed": exe_total,
                "remaining": exe_remaining,
            })

    # Step 7: Clean summary_data keys
    final_summary_data = {}
    for key, value in summary_data.items():
        if key == "lot_turns":
            new_key = "lot turns"
        else:
            new_key = key.replace('_', '')
        final_summary_data[new_key] = dict(value)

    # Step 8: Prepare monthly data
    monthly_data = (
        base_query.values("year", "month")
        .annotate(
            total_lot_turns=Sum("lot_turns"),
            total_euv_3400=Sum("EUV_3400"),
            total_exe_5000=Sum("EXE_5000")
        )
        .order_by("year", "month")
    )

    categories = []
    cumulative_lot_turns, monthly_lot_turns = [], []
    cumulative_euv_3400, monthly_euv_3400 = [], []
    cumulative_exe_5000, monthly_exe_5000 = [], []
    sum_lt = sum_euv = sum_exe = 0

    for row in monthly_data:
        label = f"{row['month']}/{row['year']}"
        lt = row["total_lot_turns"] or 0
        euv = row["total_euv_3400"] or 0
        exe = row["total_exe_5000"] or 0

        sum_lt += lt
        sum_euv += euv
        sum_exe += exe

        categories.append(label)
        monthly_lot_turns.append(round(lt, 2))
        cumulative_lot_turns.append(round(sum_lt, 2))
        monthly_euv_3400.append(round(euv, 2))
        cumulative_euv_3400.append(round(sum_euv, 2))
        monthly_exe_5000.append(round(exe, 2))
        cumulative_exe_5000.append(round(sum_exe, 2))

    # Step 9: If AJAX request, send partial response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        table_html = render_to_string("partials/wbs_table.html", {
            "summary_data": final_summary_data,
            "jpnfy_years": unique_jpnfy,
        })
        return JsonResponse({
            "table_html": table_html,
            "categories": categories,
            "monthly_lot_turns": monthly_lot_turns,
            "cumulative_lot_turns": cumulative_lot_turns,
            "monthly_euv_3400": monthly_euv_3400,
            "cumulative_euv_3400": cumulative_euv_3400,
            "monthly_exe_5000": monthly_exe_5000,
            "cumulative_exe_5000": cumulative_exe_5000,
        })

    # Step 10: Otherwise, normal page load
    return render(request, "pages/currentfy.html", {
        "factory_bu_choices": factory_bu_choices,
        "selected_factory_bu": selected_factory_bu,
        "summary_data": final_summary_data,
        "jpnfy_years": unique_jpnfy,
        "categories": categories,
        "monthly_lot_turns": monthly_lot_turns,
        "cumulative_lot_turns": cumulative_lot_turns,
        "monthly_euv_3400": monthly_euv_3400,
        "cumulative_euv_3400": cumulative_euv_3400,
        "monthly_exe_5000": monthly_exe_5000,
        "cumulative_exe_5000": cumulative_exe_5000,
    })

def department_lot_usage(request):
    factory_bu_choices = [
        f"{f} - {b}"
        for f, b in upload_data.objects.values_list("factory__name", "bu__name").distinct().order_by("factory__name", "bu__name")
        if f and b
    ]

    jpnfy_choices = (
        upload_data.objects.values_list("jpn_ytd", flat=True).distinct().order_by("-jpn_ytd")
    )
    highest_jpnfy = jpnfy_choices.first()
    selected_jpnfy = request.GET.get("jpnfy", highest_jpnfy)

    selected_factory_bu = request.GET.getlist("factory_bu")
    if not selected_factory_bu:
        selected_factory_bu = factory_bu_choices

    query = upload_data.objects.filter(jpn_ytd=selected_jpnfy)
    if selected_factory_bu:
        q_objects = Q()
        for fb in selected_factory_bu:
            try:
                factory, bu = fb.split(" - ")
                q_objects |= Q(factory__name=factory, bu__name=bu)
            except ValueError:
                continue
        query = query.filter(q_objects)

    monthly_data = (
        query.values("year", "month", "department__name")
        .annotate(
            total_lot_turns=Sum("lot_turns"),
            total_euv_3400=Sum("EUV_3400"),
            total_exe_5000=Sum("EXE_5000")
        )
        .order_by("year", "month", "department__name")
    )

    table_data = defaultdict(lambda: defaultdict(lambda: {"lot_turns": 0.0, "euv_3400": 0.0, "exe_5000": 0.0}))
    department_totals = defaultdict(lambda: {"lot_turns": 0.0, "euv_3400": 0.0, "exe_5000": 0.0})
    month_totals = defaultdict(lambda: {"lot_turns": 0.0, "euv_3400": 0.0, "exe_5000": 0.0})
    grand_totals = {"lot_turns": 0.0, "euv_3400": 0.0, "exe_5000": 0.0}

    months_set = set()
    departments_set = set()

    for row in monthly_data:
        month_str = f"{str(row['month']).zfill(2)}-{row['year']}"
        dept_name = row["department__name"]

        table_data[month_str][dept_name] = {
            "lot_turns": round(row["total_lot_turns"] or 0, 2),
            "euv_3400": round(row["total_euv_3400"] or 0, 2),
            "exe_5000": round(row["total_exe_5000"] or 0, 2),
        }

        department_totals[dept_name]["lot_turns"] += row["total_lot_turns"] or 0
        department_totals[dept_name]["euv_3400"] += row["total_euv_3400"] or 0
        department_totals[dept_name]["exe_5000"] += row["total_exe_5000"] or 0

        month_totals[month_str]["lot_turns"] += row["total_lot_turns"] or 0
        month_totals[month_str]["euv_3400"] += row["total_euv_3400"] or 0
        month_totals[month_str]["exe_5000"] += row["total_exe_5000"] or 0

        grand_totals["lot_turns"] += row["total_lot_turns"] or 0
        grand_totals["euv_3400"] += row["total_euv_3400"] or 0
        grand_totals["exe_5000"] += row["total_exe_5000"] or 0

        months_set.add(month_str)
        departments_set.add(dept_name)

    months_sorted = sorted(months_set, key=lambda x: datetime.strptime(x, "%m-%Y"))
    departments = sorted(departments_set)

    def build_series(metric_key):
        cumulative_series = []
        monthly_series = []
        for dept in departments:
            cumulative = []
            monthly = []
            total = 0
            for month in months_sorted:
                val = table_data[month][dept][metric_key]
                total += val
                cumulative.append(round(total, 2))
                monthly.append(round(val, 2))
            cumulative_series.append({"name": dept, "data": cumulative})
            monthly_series.append({"name": dept, "data": monthly})
        return cumulative_series, monthly_series

    cumulative_lt, monthly_lt = build_series("lot_turns")
    cumulative_euv, monthly_euv = build_series("euv_3400")
    cumulative_exe, monthly_exe = build_series("exe_5000")

    month_labels = []
    year_groups = []
    current_year = None
    group = {"title": "", "cols": 0}

    for entry in months_sorted:
        dt = datetime.strptime(entry, "%m-%Y")
        month_labels.append(dt.strftime("%b"))
        year = dt.strftime("%Y")
        if year != current_year:
            if group["cols"] > 0:
                year_groups.append(group)
            group = {"title": year, "cols": 1}
            current_year = year
        else:
            group["cols"] += 1

    if group["cols"] > 0:
        year_groups.append(group)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        table_html = render_to_string("partials/department_table.html", {
            "table_data": dict(table_data),
            "departments": departments,
            "month_totals": dict(month_totals),
            "department_totals": dict(department_totals),
            "grand_total": grand_totals,
            "metrics": ["lot_turns", "euv_3400", "exe_5000"],
        })
        return JsonResponse({
            "table_html": table_html,
            "categories": month_labels,
            "groups": year_groups,
            "cumulative_series_lt": cumulative_lt,
            "monthly_series_lt": monthly_lt,
            "cumulative_series_euv": cumulative_euv,
            "monthly_series_euv": monthly_euv,
            "cumulative_series_exe": cumulative_exe,
            "monthly_series_exe": monthly_exe,
        })

    return render(request, "pages/department_lot_usage.html", {
        "factory_bu_choices": factory_bu_choices,
        "selected_factory_bu": selected_factory_bu,
        "jpnfy_choices": jpnfy_choices,
        "selected_jpnfy": selected_jpnfy,
        "categories": json.dumps(month_labels),
        "groups": json.dumps(year_groups),
        "departments": departments,
        "cumulative_series_lt": json.dumps(cumulative_lt),
        "monthly_series_lt": json.dumps(monthly_lt),
        "cumulative_series_euv": json.dumps(cumulative_euv),
        "monthly_series_euv": json.dumps(monthly_euv),
        "cumulative_series_exe": json.dumps(cumulative_exe),
        "monthly_series_exe": json.dumps(monthly_exe),
        "month_totals": dict(month_totals),
        "department_totals": dict(department_totals),
        "grand_total": grand_totals,
        "metrics": ["lot_turns", "euv_3400", "exe_5000"],
    })
from collections import defaultdict
from django.shortcuts import render
from django.db.models import Sum
from .models import upload_data, BudgetData, WBS

def executive_summary_data(request):
    unique_jpnfy = list(
        upload_data.objects.values_list("jpn_ytd", flat=True).distinct().order_by("jpn_ytd")
    )
    wbs_list = WBS.objects.all().order_by("name")

    summary_data = {
        "lot_turns": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
        "EUV_3400": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
        "EXE_5000": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
    }

    for wbs in wbs_list:
        factory_bu_data = BudgetData.objects.filter(wbs=wbs).values("factory__name", "bu__name").distinct()

        for fb in factory_bu_data:
            factory_bu_name = f"{fb['factory__name']} - {fb['bu__name']}"

            # --- LOT TURNS ---
            total_budget = BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).aggregate(total_budget=Sum("lot_turns_budget"))["total_budget"] or 0
            yearly_consumed = upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).values("jpn_ytd").annotate(consumed=Sum("lot_turns")).order_by("jpn_ytd")
            consumed_by_year = {y["jpn_ytd"]: round(y["consumed"], 2) for y in yearly_consumed}
            total_consumed = sum(consumed_by_year.values())
            remaining = round(total_budget - total_consumed, 2)

            summary_data["lot_turns"][wbs.name]["budget"] += total_budget
            summary_data["lot_turns"][wbs.name]["consumed"] += total_consumed
            summary_data["lot_turns"][wbs.name]["remaining"] += remaining
            for year, value in consumed_by_year.items():
                summary_data["lot_turns"][wbs.name]["consumed_by_year"][year] += value
            summary_data["lot_turns"][wbs.name]["table_data"].append({
                "order_segment": factory_bu_name,
                "total_budget": round(total_budget, 2),
                "years_data": consumed_by_year,
                "consumed": round(total_consumed, 2),
                "remaining": remaining,
            })

            # --- EUV 3400 ---
            euv_budget = BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).aggregate(total_budget=Sum("euv3400_budget"))["total_budget"] or 0
            yearly_euv_consumed = upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).values("jpn_ytd").annotate(consumed=Sum("EUV_3400")).order_by("jpn_ytd")
            euv_consumed_by_year = {y["jpn_ytd"]: round(y["consumed"], 2) for y in yearly_euv_consumed}
            euv_total_consumed = sum(euv_consumed_by_year.values())
            euv_remaining = round(euv_budget - euv_total_consumed, 2)

            summary_data["EUV_3400"][wbs.name]["budget"] += euv_budget
            summary_data["EUV_3400"][wbs.name]["consumed"] += euv_total_consumed
            summary_data["EUV_3400"][wbs.name]["remaining"] += euv_remaining
            for year, value in euv_consumed_by_year.items():
                summary_data["EUV_3400"][wbs.name]["consumed_by_year"][year] += value
            summary_data["EUV_3400"][wbs.name]["table_data"].append({
                "order_segment": factory_bu_name,
                "total_budget": round(euv_budget, 2),
                "years_data": euv_consumed_by_year,
                "consumed": round(euv_total_consumed, 2),
                "remaining": euv_remaining,
            })

            # --- EXE 5000 ---
            exe_budget = BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).aggregate(total_budget=Sum("exe5000_budget"))["total_budget"] or 0
            yearly_exe_consumed = upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"]).values("jpn_ytd").annotate(consumed=Sum("EUV_3300")).order_by("jpn_ytd")
            exe_consumed_by_year = {y["jpn_ytd"]: round(y["consumed"], 2) for y in yearly_exe_consumed}
            exe_total_consumed = sum(exe_consumed_by_year.values())
            exe_remaining = round(exe_budget - exe_total_consumed, 2)

            summary_data["EXE_5000"][wbs.name]["budget"] += exe_budget
            summary_data["EXE_5000"][wbs.name]["consumed"] += exe_total_consumed
            summary_data["EXE_5000"][wbs.name]["remaining"] += exe_remaining
            for year, value in exe_consumed_by_year.items():
                summary_data["EXE_5000"][wbs.name]["consumed_by_year"][year] += value
            summary_data["EXE_5000"][wbs.name]["table_data"].append({
                "order_segment": factory_bu_name,
                "total_budget": round(exe_budget, 2),
                "years_data": exe_consumed_by_year,
                "consumed": round(exe_total_consumed, 2),
                "remaining": exe_remaining,
            })

    final_summary_data = {}
    for key, value in summary_data.items():
        if key == "lot_turns":
            new_key = "lot turns"  # lot_turns -> lot turns (space)
        else:
            new_key = key.replace('_', '')  # EUV_3400 -> EUV3400, EXE_5000 -> EXE5000
        final_summary_data[new_key] = dict(value)

    context = {
        "summary_data": final_summary_data,
        "jpnfy_years": unique_jpnfy,
    }

    return render(request, 'pages/executive_summary.html', context)

def lot_status(request):
    data = LotStatusData.objects.all().order_by('-uploaded_at')

    # Check if data exists before processing
    if data:
        # Count occurrences of each factory
        factory_counts = dict(Counter(record.factory for record in data))
    else:
        factory_counts = {}  # Ensure it's a dictionary even if no data exists

    context = {
        "lot_status_data": data,
        "factory_counts": factory_counts,  # Ensure factory_counts is a dictionary
        "operations_range": range(1, 16),  # Pass range for operation columns
    }
    
    return render(request, "pages/lot_status.html", context)



def contract_status(request):
    data = ContractData.objects.all().order_by('-uploaded_at')

    context = {
        "contract_data": data
    }
    
    return render(request, "pages/contract_status.html", context)


def file_explorer(request):
    folders = Folder.objects.all()
    files = UploadedFile.objects.all()

    if request.method == 'POST':
        folder_name = request.POST.get('folder_name', 'default')
        folder, _ = Folder.objects.get_or_create(name=folder_name)

        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            UploadedFile.objects.create(folder=folder, file=uploaded_file)
            return redirect('file_explorer')

    return render(request, 'pages/file_explorer.html', {
        'folders': folders,
        'files': files
    })

def delete_file(request, file_id):
    file = UploadedFile.objects.get(id=file_id)
    if file:
        file.file.delete()
        file.delete()
    return redirect('file_explorer')

def delete_folder(request, folder_id):
    folder = Folder.objects.get(id=folder_id)
    if folder:
        folder.uploadedfile_set.all().delete()
        folder.delete()
    return redirect('file_explorer')


def summary_page(request):
     # Fetch distinct JPN_FY years for table headers
    unique_jpnfy = list(
        upload_data.objects.values_list("jpn_ytd", flat=True).distinct().order_by("jpn_ytd")
    )

    # Fetch all WBS (unique)
    wbs_list = WBS.objects.all().order_by("name")

    # Initialize summary data
    summary_data = {
        "lot_turns": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
        "EUV_3400": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
        "EXE_5000": defaultdict(lambda: {"budget": 0, "consumed": 0, "remaining": 0, "consumed_by_year": defaultdict(float), "table_data": []}),
    }

    # Process each WBS
    for wbs in wbs_list:
        factory_bu_data = BudgetData.objects.filter(wbs=wbs).values("factory__name", "bu__name").distinct()

        for fb in factory_bu_data:
            factory_bu_name = f"{fb['factory__name']} - {fb['bu__name']}"

            # --- LOT TURNS ---
            total_budget = (
                BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"])
                .aggregate(total_budget=Sum("lot_turns_budget"))["total_budget"] or 0
            )
            yearly_consumed = (
                upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"])
                .values("jpn_ytd")
                .annotate(consumed=Sum("lot_turns"))
                .order_by("jpn_ytd")
           )
            consumed_by_year = {y["jpn_ytd"]: round(y["consumed"], 2) for y in yearly_consumed}
            total_consumed = sum(consumed_by_year.values())
            remaining = round(total_budget - total_consumed, 2)

            # Store WBS total values
            summary_data["lot_turns"][wbs.name]["budget"] += total_budget
            summary_data["lot_turns"][wbs.name]["consumed"] += total_consumed
            summary_data["lot_turns"][wbs.name]["remaining"] += remaining
            for year, value in consumed_by_year.items():
                summary_data["lot_turns"][wbs.name]["consumed_by_year"][year] += value

            # Store table row
            summary_data["lot_turns"][wbs.name]["table_data"].append({
                "order_segment": factory_bu_name,
                "total_budget": round(total_budget, 2),
                "years_data": consumed_by_year,
                "consumed": round(total_consumed, 2),
                "remaining": remaining,
            })

            # --- EUV 3400 ---
            euv_budget = (
                BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"])
                .aggregate(total_budget=Sum("euv3400_budget"))["total_budget"] or 0
            )
            yearly_euv_consumed = (
                upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"])
                .values("jpn_ytd")
                .annotate(consumed=Sum("EUV_3400"))
                .order_by("jpn_ytd")
            )
            euv_consumed_by_year = {y["jpn_ytd"]: round(y["consumed"], 2) for y in yearly_euv_consumed}
            euv_total_consumed = sum(euv_consumed_by_year.values())
            euv_remaining = round(euv_budget - euv_total_consumed, 2)

            summary_data["EUV_3400"][wbs.name]["budget"] += euv_budget
            summary_data["EUV_3400"][wbs.name]["consumed"] += euv_total_consumed
            summary_data["EUV_3400"][wbs.name]["remaining"] += euv_remaining
            for year, value in euv_consumed_by_year.items():
                summary_data["EUV_3400"][wbs.name]["consumed_by_year"][year] += value

            summary_data["EUV_3400"][wbs.name]["table_data"].append({
                "order_segment": factory_bu_name,
                "total_budget": round(euv_budget, 2),
                "years_data": euv_consumed_by_year,
                "consumed": round(euv_total_consumed, 2),
                "remaining": euv_remaining,
            })

            # --- EXE 5000 ---
            exe_budget = (
                BudgetData.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"])
                .aggregate(total_budget=Sum("exe5000_budget"))["total_budget"] or 0
            )
            yearly_exe_consumed = (
                upload_data.objects.filter(wbs=wbs, factory__name=fb["factory__name"], bu__name=fb["bu__name"])
                .values("jpn_ytd")
               .annotate(consumed=Sum("EUV_3300"))
                .order_by("jpn_ytd")
            )
            exe_consumed_by_year = {y["jpn_ytd"]: round(y["consumed"], 2) for y in yearly_exe_consumed}
            exe_total_consumed = sum(exe_consumed_by_year.values())
            exe_remaining = round(exe_budget - exe_total_consumed, 2)

            summary_data["EXE_5000"][wbs.name]["budget"] += exe_budget
            summary_data["EXE_5000"][wbs.name]["consumed"] += exe_total_consumed
            summary_data["EXE_5000"][wbs.name]["remaining"] += exe_remaining
            for year, value in exe_consumed_by_year.items():
                summary_data["EXE_5000"][wbs.name]["consumed_by_year"][year] += value

            summary_data["EXE_5000"][wbs.name]["table_data"].append({
                "order_segment": factory_bu_name,
                "total_budget": round(exe_budget, 2),
                "years_data": exe_consumed_by_year,
                "consumed": round(exe_total_consumed, 2),
                "remaining": exe_remaining,
            })

    # Convert defaultdict to a normal dictionary
    final_summary_data = {}
    for key, value in summary_data.items():
        if key == "lot_turns":
            new_key = "lot turns"  # lot_turns -> lot turns (space)
        else:
            new_key = key.replace('_', '')  # EUV_3400 -> EUV3400, EXE_5000 -> EXE5000
        final_summary_data[new_key] = dict(value)
        
        context = {
            "summary_data": final_summary_data,
            "jpnfy_years": unique_jpnfy,
        }

    return render(request, 'pages/summary.html', context)

def presentations(request):
    """Renders the Presentations page with upload forms."""
    return render(request, 'pages/presentations.html')
def handle_upload(request, upload_type):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Please upload a valid CSV file.")

        file_data = csv_file.read().decode('utf-8-sig')
        csv_reader = csv.DictReader(file_data.splitlines())

        if upload_type == "lot_status":
            for row in csv_reader:
                try:
                    LotStatusData.objects.create(
                        owner=row.get("owner"),
                        factory=row.get("factory"),
                        lot_id=row.get("lot_id"),
                        hold_code=row.get("hold_code"),
                        priority=int(row.get("priority")) if row.get("priority") else None,
                        current_operation=row.get("current_operation"),
                        oper1=row.get("oper1"),
                        oper2=row.get("oper2"),
                        oper3=row.get("oper3"),
                        oper4=row.get("oper4"),
                        oper5=row.get("oper5"),
                        oper6=row.get("oper6"),
                        oper7=row.get("oper7"),
                        oper8=row.get("oper8"),
                        oper9=row.get("oper9"),
                        oper10=row.get("oper10"),
                        oper11=row.get("oper11"),
                        oper12=row.get("oper12"),
                        oper13=row.get("oper13"),
                        oper14=row.get("oper14"),
                        oper15=row.get("oper15"),
                    )
                except ValueError:
                    print(f"Invalid data in row: {row}")
                    continue

        elif upload_type == "budget":
            for row in csv_reader:
                try:
                    wbs_name = row.get("WBS")
                    bu_name = row.get("BU")
                    factory_name = row.get("Factory")
                    lot_turns_budget = float(row.get("Total Lotturns Budget")) if row.get("Total Lotturns Budget") else 0
                    euv3400_budget = float(row.get("Total EUV3400 Budget")) if row.get("Total EUV3400 Budget") else 0
                    exe5000_budget = float(row.get("Total EXE5000 Budget")) if row.get("Total EXE5000 Budget") else 0

                    wbs_obj, _ = WBS.objects.get_or_create(name=wbs_name)
                    bu_obj = BU.objects.filter(name=bu_name).first() or BU.objects.create(name=bu_name)
                    factory_obj = Factory.objects.filter(name=factory_name).first() or Factory.objects.create(name=factory_name)

                    BudgetData.objects.update_or_create(
                        wbs=wbs_obj, bu=bu_obj, factory=factory_obj,
                        defaults={"lot_turns_budget": lot_turns_budget, "euv3400_budget": euv3400_budget, "exe5000_budget": exe5000_budget}
                    )
                except ValueError:
                    print(f"Invalid numerical value in row: {row}")
                    continue
                except MultipleObjectsReturned:
                    print(f"Multiple objects returned for BU: {bu_name}, WBS: {wbs_name}, or Factory: {factory_name}. Please check data consistency.")
                    continue

        elif upload_type == "contract":
            for row in csv_reader:
                try:
                    effective_date = datetime.strptime(row.get("effective_date", ""), "%d/%m/%Y").date() if row.get("effective_date") else None
                    termination_date = datetime.strptime(row.get("termination_date", ""), "%d/%m/%Y").date() if row.get("termination_date") else None
                    lot_turns = float(row.get("lot_turns", 0)) if row.get("lot_turns") else 0.0
                    euv3400 = float(row.get("euv3400", 0)) if row.get("euv3400") else 0.0
                    exe5000 = float(row.get("exe5000", 0)) if row.get("exe5000") else 0.0

                    ContractData.objects.update_or_create(
                        contract=row.get("contract"),
                        defaults={"status": row.get("status"), "effective_date": effective_date, "termination_date": termination_date,
                                  "lot_turns": lot_turns, "euv3400": euv3400, "exe5000": exe5000}
                    )
                except ValueError:
                    print(f"Invalid data in row: {row}")
                    continue

        elif upload_type == "csv":
            for row in csv_reader:
                try:
                    tmp_lot_id = row.get("tmp_lot_id")
                    status = row.get("status")

                    if status.lower() == "completed":
                        CompletedForm_Data.objects.update_or_create(tmp_lot_id=tmp_lot_id, defaults=row)
                    elif status.lower() == "active":
                        ActiveForm_Data.objects.update_or_create(tmp_lot_id=tmp_lot_id, defaults=row)
                except ValueError:
                    print(f"Invalid data in row: {row}")
                    continue

        elif upload_type == "euvdata":
            for row in csv_reader:
                try:
                    tmp_lot_id = row.get("Lot ID")
                    year_field = row.get("Year")
                    wbs_name = row.get("WBS")
                    factory_name = row.get("Factory")
                    bu_name = row.get("BU")
                    department_name = row.get("Dpmt")
                    no_of_samples = row.get("no_of_samples")

                    if not tmp_lot_id or not year_field:
                        print(f"Skipping row with missing data: {row}")
                        continue

                    try:
                        date_obj = datetime.strptime(year_field, "%Y-%m-%d")
                        year = date_obj.year
                        month = date_obj.month
                    except ValueError:
                        print(f"Invalid date format in 'Year' field: {row}")
                        continue

                    wbs_obj = WBS.objects.filter(name=wbs_name).first()
                    factory_obj = Factory.objects.filter(name=factory_name).first()
                    bu_obj = BU.objects.filter(name=bu_name).first()
                    department_obj = Department.objects.filter(name=department_name).first()

                    try:
                        no_of_samples = float(no_of_samples) if no_of_samples else None
                    except ValueError:
                        print(f"Invalid 'no_of_samples': {row}")
                        no_of_samples = None

                    record_data = {
                        "wbs": wbs_obj,
                        "factory": factory_obj,
                        "bu": bu_obj,
                        "department": department_obj,
                        "tmp_lot_id": tmp_lot_id,
                        "year": year,
                        "month": month,
                        "lot_turns": row.get("Total_Lots"),
                        "EUV_3300": row.get("3300_EUV"),
                        "EUV_3400": row.get("3400_EUV"),
                        "EXE_5000": row.get("EXE_5000"),
                        "jpn_ytd": row.get("JPN_YTD"),
                        "no_of_samples": no_of_samples,
                    }

                    upload_data.objects.update_or_create(
                        tmp_lot_id=tmp_lot_id,
                        year=year,
                        month=month,
                        defaults=record_data
                    )

                except Exception as e:
                    print(f"Error in row {row}: {e}")
                    continue

        return HttpResponse(f"CSV data for {upload_type} has been uploaded successfully.")
    return HttpResponse("Invalid request")
