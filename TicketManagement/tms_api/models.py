from datetime import datetime
from itertools import cycle
from django.db import models
from django.db.models import Count
import datetime as datetime1

available_employees = []
available_employee_cycle = cycle(available_employees)

class Ticket(models.Model):
    ticket_number = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    resolved = models.BooleanField(default=False)
    resolved_datetime = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.ticket_number)
    

    def save(self, *args, **kwargs):
        if not self.pk:
            self.allocate_ticket()
        super().save(*args, **kwargs)
         # Create a new task allocation
        if self.assigned_to is not None:
            task_allocation = TaskAllocation.objects.create(ticket=self, assigned_employee=self.assigned_to)
            task_allocation.save()

    def allocate_ticket(self):
        current_time = datetime.now().time()
        ticket_date = datetime.now().date()
        current_date = datetime1.date.today()

        # Get the list of available employees based on shift and availability
        available_employees = Employee.objects.filter(
            employeeroster__date=ticket_date,
            employeeroster__availability=True,
            employeeroster__shift_start_time__lte=current_time,
            employeeroster__shift_end_time__gte=current_time,
        ).distinct()

        if available_employees.exists():
            # assigned_tickets_counts = TaskAllocation.objects.filter(assigned_employee__in=available_employees, ticket__created_at__date=current_date).values('assigned_employee').annotate(count=Count('ticket')).order_by('count')
            assigned_tickets_counts = list(TaskAllocation.objects.filter(assigned_employee__in=available_employees,
                    allocation_date=current_date
                ).values('assigned_employee').annotate(count=Count('id')).order_by('count'))

            # if assigned_tickets_counts:
            #     assigned_employee_id = assigned_tickets_counts.first()['assigned_employee']
            #     assigned_employee = Employee.objects.get(employee_id=assigned_employee_id)
            # else:
            #     assigned_employee = available_employees.first()

            #####new one ####
            # Create a dictionary to map employee IDs to their respective count values
            # assigned_employee_counts = {count['assigned_employee']: count['count'] for count in assigned_tickets_counts}

            # Get the list of employees with a count of 0
            employees_with_zero_count = available_employees.exclude(employee_id__in=[count['assigned_employee'] for count in assigned_tickets_counts])
            for employee in employees_with_zero_count:
                assigned_tickets_counts.append({'assigned_employee': employee.employee_id, 'count': 0})

            # Sort the assigned_tickets_counts by count in ascending order
            assigned_tickets_counts.sort(key=lambda x: x['count'])

            if assigned_tickets_counts:
                assigned_employee_id = assigned_tickets_counts[0]['assigned_employee']
                assigned_employee = Employee.objects.get(employee_id=assigned_employee_id)
            else:
                assigned_employee = available_employees.first()

            self.assigned_to = assigned_employee
        else:
            self.assigned_to = None


   
class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EmployeeRoster(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    date = models.DateField()
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee} - {self.date}"


class TaskAllocation(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    assigned_employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    allocation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Ticket: {self.ticket.ticket_number} - Assigned to: {self.assigned_employee.name}"   