from django.views.generic import TemplateView
from web_project import TemplateLayout
from .models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions
from django.http import JsonResponse
from datetime import datetime
from django.db import connection

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardsView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context
    


    

def PieCountbySeverity(request):
    query = '''
        SELECT severity_level, COUNT(*) as count
        FROM fire_incident
        GROUP BY severity_level
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    data = {severity: count for severity, count in rows} if rows else {}
    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year
    result = {month: 0 for month in range(1, 13)}
    incidents_per_month = Incident.objects.filter(date_time__year=current_year).values_list('date_time', flat=True)
    for date_time in incidents_per_month:
        result[date_time.month] += 1
    month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    result_named = {month_names[k]: v for k, v in result.items()}
    return JsonResponse(result_named)

def map_station(request):
    stations = FireStation.objects.values('name', 'latitude', 'longitude')
    for fs in stations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
    return render(request, 'map_station.html', {'fireStations': list(stations)})

def map_incidents(request):
    fireIncidents = Incident.objects.select_related('location').values(
        'location__city', 'location__latitude', 'location__longitude',
        'description', 'date_time', 'severity_level'
    )
    incident_list = [{
        'city': fi['location__city'],
        'latitude': float(fi['location__latitude']),
        'longitude': float(fi['location__longitude']),
        'description': fi['description'],
        'date': fi['date_time'].strftime('%Y-%m-%d %H:%M') if fi['date_time'] else 'N/A',
        'severity': fi['severity_level']
    } for fi in fireIncidents]

    cities = Incident.objects.select_related('location').values_list('location__city', flat=True).distinct()
    return render(request, 'map_incidents.html', {'fireIncidents': incident_list, 'cities': cities})

def MultilineIncidentTop3Country(request):
    query = '''
        SELECT fl.country, strftime('%m', fi.date_time) AS month, COUNT(fi.id) AS incident_count
        FROM fire_incident fi
        JOIN fire_locations fl ON fi.location_id = fl.id
        WHERE fl.country IN (
            SELECT fl_top.country
            FROM fire_incident fi_top
            JOIN fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY fl_top.country
            ORDER BY COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
        GROUP BY fl.country, month
        ORDER BY fl.country, month;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    for country, month, count in rows:
        result.setdefault(country, {m: 0 for m in months})[month] = count
    while len(result) < 3:
        result[f"Country {len(result)+1}"] = {m: 0 for m in months}
    for country in result:
        result[country] = dict(sorted(result[country].items()))
    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
        SELECT fi.severity_level, strftime('%m', fi.date_time) AS month, COUNT(fi.id)
        FROM fire_incident fi
        GROUP BY fi.severity_level, month
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    for level, month, count in rows:
        result.setdefault(str(level), {m: 0 for m in months})[month] = count
    for level in result:
        result[level] = dict(sorted(result[level].items()))
    return JsonResponse(result)
