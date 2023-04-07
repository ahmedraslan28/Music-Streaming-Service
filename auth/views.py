from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


from . import serializers

User = get_user_model()


class Login(generics.CreateAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'data': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_admin': user.is_staff,
                    'is_artist': user.is_artist,
                    'is_premium': user.is_premium,
                }
            })

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class Register(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"http://localhost:8000/api/auth/email-confirm/{uid}/{token}"
        send_mail(
            'Confirm Your Email',
            f'Please click on this link to Confirm your mail: {reset_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
        )

        return Response({
            'success': 'if the email exist the confirmation Email will sent to the specified email address',
            "message": "Token sent to email!"
        })


class EmailConfirm(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if (user.is_active):
                return Response({"message": "invalid activate link!"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            message = ""
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": message + "successfully activated",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'data': {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_admin': user.is_staff,
                    'is_artist': user.is_artist,
                    'is_premium': user.is_premium,
                    'email': user.email
                }
            })
        return Response({'error': 'Invalid activation URL.'})


class ForgotPassword(generics.CreateAPIView):
    serializer_class = serializers.ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            token = default_token_generator.make_token(user)
            reset_url = f"http://localhost:8000/api/auth/reset-password/{uid}/{token}"
            send_mail(
                'Reset Your Password',
                f'Please click on this link to reset your password: {reset_url}',
                settings.EMAIL_HOST_USER,
                [email],
            )
        except User.DoesNotExist:
            return Response({'no user found with given email'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': 'if the email exist the Password reset Email will sent to the specified email address',
            "message": "Token sent to email!"
        })


class ResetPassword(generics.CreateAPIView):
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'success': 'Password has been reset.'})
        return Response({'error': 'Invalid reset URL.'})


class UpdatePassword(generics.GenericAPIView):
    serializer_class = serializers.UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = get_object_or_404(User, pk=self.request.user.id)
        return self.queryset

    def patch(self, request, *args, **kwargs):
        user = self.get_queryset()

        refresh = RefreshToken.for_user(user)
        context = {"user": user}
        serializer = self.serializer_class(
            user, data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "password reseted successfuly",
            "token": str(refresh.access_token)
        })
