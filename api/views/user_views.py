from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt


from rest_framework import generics, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status


import stripe

from ..serializers import (
    UserSerializer, TrackSerializer,
    PlaylistSerializer, AlbumSerializer,
    DeletedPlaylistsSerializer)
from ..models import (
    SubscriptionPlan, User_SubscriptionPlan, Track,
    LikedTrack, Playlist, LikedPlaylist, Album, LikedAlbum,
    Follower,)

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


class UsersList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False, is_active=True).all()
    permission_classes = [IsAdminUser]


class UsersDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer
    queryset = User.objects.filter(is_artist=False, is_active=True).all()
    lookup_field = 'id'


class UserProfile(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        self.queryset = self.request.user
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_follow(request, id):
    user_to_follow = User.objects.filter(pk=id)

    if not user_to_follow.exists():
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user_to_follow = user_to_follow[0]
    if user_to_follow == request.user:
        return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.following.filter(followed=user_to_follow).exists():
        return Response({"detail": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

    Follower.objects.create(
        follower=request.user,
        followed=user_to_follow
    )

    return Response({"message": "followed successfully"}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_unfollow(request, id):
    user_to_unfollow = User.objects.filter(pk=id)

    if not user_to_unfollow.exists():
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user_to_unfollow = user_to_unfollow[0]
    if user_to_unfollow == request.user:
        return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    if not request.user.following.filter(followed=user_to_unfollow).exists():
        return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

    Follower.objects.get(follower=request.user,
                         followed=user_to_unfollow).delete()

    return Response({"message": "unfollowed successfully"}, status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout(request, plan_id):
    if request.user.is_premium:
        return Response({"message": "your are already a premium user"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    try:
        plan = get_object_or_404(SubscriptionPlan, pk=plan_id)
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
            success_url='http://127.0.0.1:8000/api/users/upgrade/success/',
            cancel_url='http://127.0.0.1:8000/api/users/upgrade/cancel/',
        )
    except Exception as e:
        return Response({"message": f"{str(e)}"}, status=400)

    return redirect(checkout_session.url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def success(request):
    return Response({"message": "congratulations your account upgraded successfuly"}, status=200)


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
