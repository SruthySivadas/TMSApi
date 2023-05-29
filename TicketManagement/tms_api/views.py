
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Employee, EmployeeRoster, Ticket
from .serializers import EmployeeRosterSerializer, EmployeeSerializer, TicketReadSerializer, TicketUpdateSerializer,EmployeeTicketReadSerializer
from django.db.models import Count, Q
from django.http import JsonResponse
from datetime import datetime,timedelta
from django.utils import timezone


@api_view(['GET', 'POST'])
@method_decorator(csrf_exempt, name='dispatch')
def ticket_list(request):
    if request.method == 'GET':
        tickets = Ticket.objects.all()
        serializer = TicketReadSerializer(tickets, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TicketUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@method_decorator(csrf_exempt, name='dispatch')
def ticket_detail(request, pk):
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response(status=404)
    
    if request.method == 'GET':
        serializer = TicketReadSerializer(ticket)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = TicketUpdateSerializer(ticket, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        ticket.delete()
        return Response(status=204)

@api_view(['GET', 'POST'])
@method_decorator(csrf_exempt, name='dispatch')
def employee_list(request):
    if request.method == 'GET':
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':    
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@method_decorator(csrf_exempt, name='dispatch')
def employee_detail(request, pk):
    try:
       employee = Employee.objects.get(pk=pk)
    except employee.DoesNotExist:
        return Response(status=404)
    
    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        employee.delete()
        return Response(status=204)

@api_view(['GET', 'POST'])
@method_decorator(csrf_exempt, name='dispatch')
def employee_roster_list(request):
    if request.method == 'GET':
        rosters = EmployeeRoster.objects.all()
        serializer = EmployeeRosterSerializer(rosters, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        employee_id = request.data.get('employee')
    
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
    
        serializer = EmployeeRosterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@method_decorator(csrf_exempt, name='dispatch')
def employee_roster_detail(request, pk):
    try:
        roster = EmployeeRoster.objects.get(id=pk)
    except EmployeeRoster.DoesNotExist:
        return Response(status=404)
    
    if request.method == 'GET':
        serializer = EmployeeRosterSerializer(roster)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = EmployeeRosterSerializer(roster, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        roster.delete()
        return Response(status=204)

@api_view(['GET'])
def employee_employee_roster_list(request,employee_id):
    print("hhhh",employee_id)
    if request.method == 'GET':
        rosters = EmployeeRoster.objects.filter(employee_id=employee_id)
        serializer = EmployeeRosterSerializer(rosters, many=True)
        return Response(serializer.data)

def ticket_stats_in_date_range(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_datetime = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)
        print(start_datetime,end_datetime)

        tickets = Ticket.objects.filter(created_at__range=[start_datetime, end_datetime])

        # Get the total number of tickets
        total_tickets = tickets.count()

        # Get the number of resolved tickets
        resolved_tickets = tickets.filter(resolved=True).count()

        # Get the number of pending tickets
        pending_tickets = tickets.filter(resolved=False).count()

        # Get the number of unassigned tickets
        unassigned_tickets = tickets.filter(assigned_to=None).count()

        # Construct the response JSON
        response_data = {
            'total_tickets': total_tickets,
            'resolved_tickets': resolved_tickets,
            'pending_tickets': pending_tickets,
            'unassigned_tickets': unassigned_tickets,
        }

        return JsonResponse(response_data,status=200)

    else:
        return JsonResponse({'error': 'Invalid request method.'})

def employee_ticket_stats_in_date_range(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_datetime = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=400)

        employees = Employee.objects.annotate(
        total_assigned_tickets=Count('ticket', filter=Q(ticket__created_at__range=(start_datetime, end_datetime))),
        total_solved_tickets=Count('ticket', filter=Q(ticket__resolved=True, ticket__created_at__range=(start_datetime, end_datetime))),
        total_pending_tickets=Count('ticket', filter=Q(ticket__resolved=False, ticket__created_at__range=(start_datetime, end_datetime))),
        )

        employee_data = []
        for employee in employees:
            employee_info = {
                'employee_id': employee.employee_id,
                'employee_name': employee.name,
                'total_assigned_tickets': employee.total_assigned_tickets if hasattr(employee, 'total_assigned_tickets') else 0,
                'total_solved_tickets': employee.total_solved_tickets if hasattr(employee, 'total_solved_tickets') else 0,
                'total_pending_tickets': employee.total_pending_tickets if hasattr(employee, 'total_pending_tickets') else 0,
            }
            employee_data.append(employee_info)
        # Construct the response JSON
        response_data = {'employees': employee_data}

        return JsonResponse(response_data, status=200)

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@api_view(['GET'])
def employee_ticket_list(request, employee_id):
    tickets = Ticket.objects.filter(assigned_to_id=employee_id)
    serializer = EmployeeTicketReadSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def update_ticket_resolved(request, ticket_id):
    try:
        ticket = Ticket.objects.get(ticket_number=ticket_id)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=404)

    # Update ticket status as resolved and set resolved time
    ticket.resolved = True
    ticket.resolved_datetime = datetime.now()
    ticket.save()

    serializer = TicketUpdateSerializer(ticket)
    return Response(serializer.data)

@api_view(['POST'])
@method_decorator(csrf_exempt, name='dispatch')
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    print("request>>>>>>>>>>",request,username,password)

    # Authenticate user
    user = authenticate(request, username=username, password=password)
    print("user>>>>>>>>>>",user)
    if user is not None:
        # Login the user
        login(request, user)
        return Response({'message': 'Login successful'})
    else:
        return Response({'message': 'Invalid credentials'}, status=401)