

# views.py


from django.db.models import Count

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer

from rest_framework.permissions import IsAuthenticated

class EventAPIView(APIView):
    permission_classes = []  # No permissions required
    authentication_classes = []  # No authentication required

    def get(self, request, branch_id=None, *args, **kwargs):
        """
        Handle GET requests: List all events or events by branch_id.
        """
        try:
            # Fetch events based on branch_id if provided
            if branch_id is not None:
                events = Event.objects.filter(branch_id=branch_id)
                if not events.exists():
                    return Response(
                        {"message": f"No events found for branch ID {branch_id}."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                events = Event.objects.all()

            # Serialize the events
            serializer = EventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventPartAPIView(APIView):
    permission_classes = []  # No permissions required
    authentication_classes = []  # No authentication required

    def get(self, request, event_id=None, branch_id=None, *args, **kwargs):
        try:
            # Case 1: Get single event by ID
            if event_id is not None:
                try:
                    event = Event.objects.get(id=event_id)
                    serializer = EventSerializer(event)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Event.DoesNotExist:
                    return Response(
                        {"message": f"Event with ID {event_id} not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Case 2: Get events by branch_id
            if branch_id is not None:
                events = Event.objects.filter(branch_id=branch_id)
                if not events.exists():
                    return Response(
                        {"message": f"No events found for branch ID {branch_id}."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            # Case 3: Get all events
            else:
                events = Event.objects.all()

            # Add optional filters from query parameters
            event_date = request.query_params.get('date')
            if event_date:
                events = events.filter(date=event_date)

            event_type = request.query_params.get('type')
            if event_type:
                events = events.filter(event_type=event_type)

            # Order events by date
            events = events.order_by('date')

            serializer = EventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventAdminView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            pk = kwargs.get('pk')
            print("PK:", pk)

            # Filter events based on user role
            if user.role == 'branch_manager':
                events = Event.objects.filter(branch=user.branch)
            elif pk == "admin":  # For admin route
                events = Event.objects.all()
            elif pk is None or pk == "7":
                events = Event.objects.all()
            else:
                events = Event.objects.filter(branch=pk)

            # Add participant count annotation
            events = events.annotate(participant_count=Count('participants'))

            # Serialize events
            serializer = EventSerializer(events, many=True)

            # Add participant count to serialized data dynamically
            for event, data in zip(events, serializer.data):
                data["participant_count"] = event.participant_count

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, *args, **kwargs):
        try:
            data = request.data.copy()


            if 'branch' in data and isinstance(data['branch'], str):
                data['branch'] = int(data['branch'])

            if 'date' in data and isinstance(data['date'], str):
                if len(data['date']) == 16:  # אם לא נשלחו שניות
                    data['date'] += ":00"  # הוסף שניות בסוף

            # הוסף את המשתמש המחובר לשדה created_by
            data['created_by'] = request.user.id

            # יצירת Serializer עם הנתונים המתוקנים
            serializer = EventSerializer(data=data)
            if serializer.is_valid():
                # שמירת האירוע במסד הנתונים
                event = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # החזרת שגיאות אימות אם הנתונים לא תקינים
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as ve:
            return Response(
                {"error": "Invalid value in the data", "details": str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        try:
            event_id = kwargs.get('pk')
            if not event_id:
                return Response(
                    {'error': 'Event ID is required to update an event'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            event = Event.objects.filter(id=event_id).first()
            if not event:
                return Response(
                    {'error': 'Event not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = EventSerializer(event, data=request.data)
            if serializer.is_valid():
                event = serializer.save()
                return Response(EventSerializer(event).data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, *args, **kwargs):
        try:
            event_id = kwargs.get('pk')
            if not event_id:
                return Response(
                    {'error': 'Event ID is required to partially update an event'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            event = Event.objects.filter(id=event_id).first()
            if not event:
                return Response(
                    {'error': 'Event not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = EventSerializer(event, data=request.data, partial=True)
            if serializer.is_valid():
                event = serializer.save()
                return Response(EventSerializer(event).data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "User must be authenticated"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if request.user.role == "employee":
                return Response(
                    {"error": "user must be an admin"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            event_id = kwargs.get('pk')

            if not event_id:
                return Response(
                    {'error': 'Event ID is required to delete an event'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            event = Event.objects.filter(id=event_id).first()
            if not event:
                return Response(
                    {'error': 'Event not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            event.delete()
            return Response(
                {'message': f'Event with ID {event_id} deleted successfully'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




