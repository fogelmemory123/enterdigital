from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Participant
from events.models import Event
from .serializers import ParticipantSerializer
from django.shortcuts import get_object_or_404
import smtplib
from email.mime.text import MIMEText
import ssl
import certifi


class ParticipantAPIView(APIView):
    def get(self, request, event_id=None):
        try:
            event = get_object_or_404(Event, id=event_id)
            participants = Participant.objects.filter(event=event)

            if not participants.exists():
                return Response({
                    "message": f"No participants found for event {event_id}",
                    "participants": []
                }, status=status.HTTP_200_OK)

            serializer = ParticipantSerializer(participants, many=True)
            return Response({
                "message": "Participants retrieved successfully",
                "participants": serializer.data,
                "participant_count": len(serializer.data)
            }, status=status.HTTP_200_OK)

        except Event.DoesNotExist:
            return Response({
                "error": f"Event with ID {event_id} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "error": "An error occurred while fetching participants",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, event_id=None):
        try:
            print("Received data:", request.data)

            # Prepare data for serializer
            modified_data = {
                'event': event_id,  # Use event_id from URL
                'name': request.data.get('name'),
                'email': request.data.get('email')
            }

            serializer = ParticipantSerializer(data=modified_data)
            if serializer.is_valid():
                participant = serializer.save()

                # Get event details for email
                event = Event.objects.get(id=event_id)

                # Send confirmation email
                ssl_context = ssl.create_default_context(cafile=certifi.where())

                try:
                    # Format the email message in Hebrew
                    email_body = f"""
                שלום {participant.name},

                תודה שנרשמת לאירוע "{event.description}".

                פרטי האירוע:
                תאריך: {event.date}
                מיקום: {event.branch}

                נתראה באירוע!

                בברכה,
                צוות Enter Workshops
                    """

                    msg = MIMEText(email_body, 'plain', 'utf-8')  # Add UTF-8 encoding for Hebrew
                    msg['Subject'] = f'הרשמה לאירוע - {event.description}'
                    msg['From'] = 'enterworkshops@gmail.com'
                    msg['To'] = request.data.get('email')

                    with smtplib.SMTP('smtp.gmail.com', 587) as server:
                        server.starttls(context=ssl_context)
                        server.login('enterworkshops@gmail.com', '*******')
                        server.send_message(msg)
                    print("Email sent successfully")
                except Exception as email_error:
                    print(f"Email sending failed: {email_error}")
                return Response({
                    "message": "Registration successful",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "error": "Invalid data provided",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Event.DoesNotExist:
            return Response({
                "error": f"Event with ID {event_id} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "error": "An error occurred during registration",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self, request, event_id=None, participant_id=None):
        try:
            # First verify that both event and participant exist
            event = get_object_or_404(Event, id=event_id)
            participant = get_object_or_404(Participant, id=participant_id, event=event)

            # Store participant info for the response
            participant_name = participant.name

            # Delete the participant
            participant.delete()

            return Response({
                "message": f"Participant {participant_name} successfully deleted from event {event.description}",
                "participant_id": participant_id
            }, status=status.HTTP_200_OK)

        except Event.DoesNotExist:
            return Response({
                "error": f"Event with ID {event_id} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        except Participant.DoesNotExist:
            return Response({
                "error": f"Participant with ID {participant_id} not found in event {event_id}"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "error": "An error occurred while deleting the participant",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
