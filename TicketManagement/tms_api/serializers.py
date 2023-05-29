from rest_framework import serializers
from .models import Employee, EmployeeRoster, Ticket


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class EmployeeRosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRoster
        fields = '__all__'

class TicketReadSerializer(serializers.ModelSerializer):
    assigned_to = EmployeeSerializer()
    class Meta:
        model = Ticket
        fields = '__all__'

# class TicketUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ticket
#         exclude = ('ticket_number','created_at','updated_at','resolved_datetime','resolved','assigned_to')

class TicketUpdateSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    resolved_datetime = serializers.ReadOnlyField()
    resolved = serializers.ReadOnlyField()
    assigned_to = EmployeeSerializer(read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'


class EmployeeTicketReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        exclude=['assigned_to']
