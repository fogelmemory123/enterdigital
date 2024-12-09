# views.py
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
User = get_user_model()
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import F

class UserBirthdayView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def get(self, request, branch_id=None, *args, **kwargs):
        try:
            if branch_id==7:
                users = User.objects.all().values('id', 'username', 'birthday', 'branch')
                return Response(list(users), status=status.HTTP_200_OK)

            elif branch_id is not None:
                # Filter users by branch_id
                users = User.objects.filter(branch__id=branch_id).values('id', 'username', 'birthday', 'branch')
                if not users:
                    return Response(
                        {'message': f'No users found for branch ID {branch_id}.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Return all users
                users = User.objects.all().values('id', 'username', 'birthday', 'branch')

            return Response(list(users), status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'An unexpected error occurred', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# users/views.py


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'branch': user.branch.id if user.branch else None
                }
            })
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterView(APIView):
    def post(self, request):
        try:
            # Get data from request
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            role = request.data.get('role', 'employee')  # default to employee
            branch_id = request.data.get('branch')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            birthday = request.data.get('birthday')

            # Validate username is unique
            if User.objects.filter(username=username).exists():
                return Response(
                    {"error": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                role=role,
                branch_id=branch_id,
                first_name=first_name,
                last_name=last_name,
                birthday=birthday
            )

            # Return user data
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError

class UserBirthdayAdminView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:

            user = request.user
            if not user.branch:
                return Response(
                    {"error": "User branch not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            pk = kwargs.get('pk')
            if pk==7 or pk is None:
                users = User.objects.annotate(
                    city=F('branch__city')
                ).values(
                    'id',
                    'username',
                    'first_name',
                    'last_name',
                    'birthday',
                    'city',
                    'branch'
                )
            elif pk:
                users = User.objects.filter(
                    branch=pk
                ).annotate(
                    city=F('branch__city')
                ).values(
                    'id',
                    'username',
                    'first_name',
                    'last_name',
                    'birthday',
                    'city',
                    'branch'
                )
            else:
              users = User.objects.filter(
                branch=user.branch
            ).annotate(
                city=F('branch__city')
            ).values(
                'id',
                'username',
                'first_name',
                'last_name',
                'birthday',
                'city',
                'branch'
            )

            user_list = []
            for user in users:
                birthday = user['birthday'].strftime('%Y-%m-%d') if user['birthday'] else None
                user_data = {
                    'id': user['id'],
                    'username': user['username'],
                    'name': user['first_name'],
                    'lastname': user['last_name'],
                    'birthday': birthday,
                    'branch': user['branch'],
                    'city': user['city']
                }
                user_list.append(user_data)

            return Response(user_list, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in get_birthdays: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching birthdays"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, *args, **kwargs):
        try:
            required_fields = ['username', 'first_name', 'last_name', 'password', 'birthday', 'branch']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"error": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            request.data['password'] = make_password(request.data['password'])

            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():

                user = serializer.save()
                return Response(
                    UserSerializer(user).data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Error in create_user: {str(e)}")
            return Response(
                {"error": "An error occurred while creating the user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get('pk')
            if not user_id:
                return Response(
                    {"error": "User ID is required to update a user"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.filter(id=user_id, branch=request.user.branch).first()
            if not user:
                return Response(
                    {"error": "User not found or does not belong to your branch"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = UserSerializer(user, data=request.data, partial=False)  # Use partial=True for partial updates
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error in update_user: {str(e)}")
            return Response(
                {"error": "An error occurred while updating the user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            if request.user.role=="employee":
                return Response(
                    {"error": "user must be an admin"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_id = kwargs.get('pk')
            if not user_id:
                return Response(
                    {"error": "User ID is required to delete a user"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response(
                    {"error": "User not found or does not belong to your branch"},
                    status=status.HTTP_404_NOT_FOUND
                )

            user.delete()
            return Response(
                {"message": f"User with ID {user_id} deleted successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Error in delete_user: {str(e)}")
            return Response(
                {"error": "An error occurred while deleting the user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class GetUserNameView(APIView):
            """
            API view to return the username of the currently logged-in user.
            """
            permission_classes = [IsAuthenticated]

            def get(self, request, *args, **kwargs):
                username = request.user.username
                return Response({'username': username})