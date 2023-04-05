from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..serializers import UserSerializer

User = get_user_model()


# add permissions
class UsersList(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False)
    # permission_classes = [IsAdminUser]


class UsersDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False)
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


class UserProfile(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = get_object_or_404(User, pk=self.request.user.id)
        return self.queryset

    def get(self, request):
        obj = self.get_queryset()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def patch(self, request):
        obj = self.get_queryset()
        serializer = self.get_serializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
