from django.http import JsonResponse, Http404
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend


from rest_framework import generics, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


import stripe

from ..serializers import (
    UserSerializer, TrackSerializer,
    PlaylistSerializer, AlbumSerializer,
    DeletedPlaylistsSerializer, FollowersSerializer,
    FollowingSerializer, NotificationSerializer)
from ..models import (
    SubscriptionPlan, User_SubscriptionPlan, Track,
    LikedTrack, Playlist, LikedPlaylist, Album, LikedAlbum,
    Follower,)
from ..filters import *

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


class UsersList(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsAdminUser]

    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter


class UsersDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    lookup_field = 'id'


class UsersPlaylists(generics.ListAPIView):
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        get_object_or_404(User, pk=self.kwargs['id'])
        self.queryset = Playlist.objects.filter(user=self.kwargs['id'])
        return self.queryset


class UserProfile(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = User.objects.filter(
            pk=self.request.user.pk).prefetch_related('followers').prefetch_related('following')[0]
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


class UserSavedTracks(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TrackSerializer

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        liked_tracks = LikedTrack.objects.filter(user=self.request.user)
        track_ids = liked_tracks.values_list('track_id', flat=True)
        self.queryset = Track.objects.filter(id__in=track_ids)

        return self.queryset

    def get(self, request):
        tracks = self.get_queryset()
        serializer = self.get_serializer(tracks, many=True)
        return Response(serializer.data)


class UserSavedPlaylists(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = PlaylistSerializer

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        liked_playlists = LikedPlaylist.objects.filter(user=self.request.user)
        playlist_ids = liked_playlists.values_list('playlist_id', flat=True)
        self.queryset = Playlist.objects.prefetch_related('tracks').filter(
            (Q(id__in=playlist_ids) | Q(user=self.request.user)), is_deleted=False)

        return self.queryset

    def get(self, request):
        playlists = self.get_queryset()
        serializer = self.get_serializer(playlists, many=True)
        return Response(serializer.data)


class UserSavedAlbums(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = AlbumSerializer

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        liked_albums = LikedAlbum.objects.filter(user=self.request.user)
        album_ids = liked_albums.values_list('album_id', flat=True)
        print(album_ids)
        self.queryset = Album.objects.filter(id__in=album_ids)

        return self.queryset

    def get(self, request):
        album = self.get_queryset()
        serializer = self.get_serializer(album, many=True)
        return Response(serializer.data)


class UserDeletedPlaylists(generics.ListAPIView):
    serializer_class = DeletedPlaylistsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        self.queryset = Playlist.objects.filter(
            user=self.request.user, is_deleted=True)
        return self.queryset


class UserDeletedPlaylistsDetails(views.APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        get_object_or_404(Playlist, pk=self.kwargs['id'],
                          user=self.request.user, is_deleted=True)
        queryset = Playlist.objects.filter(pk=self.kwargs['id'],
                                           user=self.request.user, is_deleted=True)
        return queryset

    def get(self, request, id):
        obj = self.get_queryset()[0]
        serializer = DeletedPlaylistsSerializer(obj)
        return Response(serializer.data)

    def post(self, request, id):
        obj = self.get_queryset()[0]
        obj.is_deleted = False
        obj.deleted_at = None
        obj.save()
        return Response({"message": "The Playlist Restored successfully !"})


class UserFollower(generics.ListAPIView):
    serializer_class = FollowersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        user_id = self.kwargs['id']
        if not User.objects.filter(pk=user_id).exists():
            raise Http404

        self.queryset = Follower.objects.filter(
            followed=user_id).prefetch_related('follower')
        return self.queryset


class UserFollowing(generics.ListAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        user_id = self.kwargs['id']
        if not User.objects.filter(pk=user_id).exists():
            raise Http404

        self.queryset = Follower.objects.filter(
            follower=user_id).prefetch_related('followed')
        return self.queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_follow(request, id):
    user_to_follow = User.objects.filter(pk=id)
    user = request.user

    if not user_to_follow.exists():
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user_to_follow = user_to_follow[0]
    if user_to_follow == user:
        return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if user.following.filter(followed=user_to_follow).exists():
        return Response({"detail": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

    Follower.objects.create(
        follower=user,
        followed=user_to_follow
    )
    user.following_count += 1
    user_to_follow.followers_count += 1
    user.save()
    user_to_follow.save()

    Notification.objects.create(
        reciever=user_to_follow,
        message=f'{user.first_name} followed {user_to_follow.first_name}'
    )

    return Response({"message": "followed successfully"}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_unfollow(request, id):
    user_to_unfollow = User.objects.filter(pk=id)
    user = request.user
    if not user_to_unfollow.exists():
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user_to_unfollow = user_to_unfollow[0]
    if user_to_unfollow == user:
        return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if not user.following.filter(followed=user_to_unfollow).exists():
        return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

    Follower.objects.get(follower=user,
                         followed=user_to_unfollow).delete()

    user.following_count -= 1
    user_to_unfollow.followers_count -= 1
    user.save()
    user_to_unfollow.save()

    return Response({"message": "unfollowed successfully"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout(request, plan_id):
    user = request.user
    if user.is_premium:
        return Response({"message": "your are already a premium user"}, status=status.HTTP_406_NOT_ACCEPTABLE)

    try:
        plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
        user_plan_id = f"{user.id}:{plan.id}"
        uid = urlsafe_base64_encode(force_bytes(user_plan_id))
        token = default_token_generator.make_token(user)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(plan.price * 100),
                        'product_data': {
                            'name': plan.name + " plan"
                        }
                    },
                    'quantity': 1
                }
            ],
            metadata={
                "user": request.user.id,
                "plan": plan.id
            },
            mode='payment',
            success_url=f'http://127.0.0.1:8000/api/users/upgrade/{uid}/{token}/success/',
            cancel_url='http://127.0.0.1:8000/api/users/upgrade/cancel/',
        )
    except Exception as e:
        return Response({"message": f"{str(e)}"}, status=400)

    return redirect(checkout_session.url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def success(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_id, plan_id = uid.split(':')
        user = User.objects.get(pk=user_id)
        plan = SubscriptionPlan.objects.get(pk=plan_id)

        if default_token_generator.check_token(user, token):
            user.is_premium = True
            user.save()
            end_date = timezone.now() + timezone.timedelta(days=30)
            User_SubscriptionPlan.objects.create(
                user_id=user_id, plan_id=plan_id, end_date=end_date)
            return Response({"success": "congratulations your account upgraded successfuly"}, status=200)
        return Response({'error': 'Invalid URL.'}, status=400)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist, SubscriptionPlan.DoesNotExist):
        return Response({'error': 'Invalid URL.'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel(request):
    return Response({"message": "the payment canceled successfuly"}, status=200)


@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_KEY
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user']
        plan_id = session['metadata']['plan']
        user = User.objects.get(pk=user_id)
        user.is_premium = True
        user.save()

        end_date = timezone.now() + timezone.timedelta(days=30)
        User_SubscriptionPlan.objects.create(
            user_id=user_id, plan_id=plan_id, end_date=end_date)

    return Response(status=200)


class UserNotifications(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if self.queryset:
            return self.queryset
        self.queryset = Notification.objects.filter(reciever=self.request.user)

        return self.queryset


@api_view(['GET'])
def say_hello(request):
    expired_subscriptions = User_SubscriptionPlan.objects.filter(
        end_date__lt=timezone.now())
    user_ids = expired_subscriptions.values_list('user_id', flat=True)
    User.objects.filter(id__in=user_ids).update(is_premium=False)
    data = list(expired_subscriptions.values())
    return JsonResponse(data, safe=False)
