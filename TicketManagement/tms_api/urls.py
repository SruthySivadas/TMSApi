from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.ticket_list, name='ticket-list'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket-detail'),
    path('employees/', views.employee_list, name='employee-list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee-detail'),
    path('employee-roster/', views.employee_roster_list, name='employee-roster-list'),
    path('employee-roster/<int:pk>/', views.employee_roster_detail, name='employee-roster-detail'),
    path('employee-roster/employee/<int:employee_id>/', views.employee_employee_roster_list, name='employee_employee_roster_list'),
    path('login/', views.login_view, name='login'),
   
    path('tickets-stats/date-range/', views.ticket_stats_in_date_range, name='ticket_stats'),
    path('employee-ticket-stats/', views.employee_ticket_stats_in_date_range, name='employee_ticket_stats'),
    path('employees/<int:employee_id>/tickets/', views.employee_ticket_list, name='employee-ticket-list'),
    path('tickets/<int:ticket_id>/resolve/', views.update_ticket_resolved, name='employee-ticket-list'),

]