
from .serializers import BranchSerializer

from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Branch

class BranchListCreateAPIView(APIView):
    def get(self, request, id=None, *args, **kwargs):
        if id is not None:
            try:
                branch = Branch.objects.get(id=id)
                serializer = BranchSerializer(branch)
            except Branch.DoesNotExist:
                return Response(
                    {"error": "Branch not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            branches = Branch.objects.all()
            serializer = BranchSerializer(branches, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class BranchAdminView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user

            # Check if the user has a role attribute
            if not hasattr(user, 'role'):
                return Response(
                    {'error': 'User role is not defined.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch branches based on the user's role
            if user.role == 'branch_manager':
                if not hasattr(user, 'branch'):
                    return Response(
                        {'error': 'Branch manager is not associated with a branch.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                branches = Branch.objects.filter(city=user.branch)
            elif user.role == 'admin':
                branches = Branch.objects.all()
            else:
                return Response(
                    {'error': 'User does not have permission to view branches.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = BranchSerializer(branches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

            # Serialize branch data



        except Exception as e:
            return Response(
                {'error': 'An error occurred: ' + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



