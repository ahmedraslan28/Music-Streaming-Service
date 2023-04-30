from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.hashers import make_password
from api.models import User, Artist, SubscriptionPlan, Category, User_SubscriptionPlan

users = [
    User(
        email="free_user@example.com",
        password=make_password("user"),
        username="free_user",
        first_name="ahmed",
        last_name="raslan",
        is_male="True",
    ),
    User(
        email="premium_user@example.com",
        password=make_password("user"),
        username="premium_user",
        first_name="shady",
        last_name="hossam",
        is_male="True",
        is_premium="True"
    ),
    User(
        email="admin@example.com",
        password=make_password("admin"),
        username="admin_user",
        first_name="abdo",
        last_name="hussien",
        is_male="True",
        is_staff="True"
    ),
    User(
        email="artist@example.com",
        password=make_password("artist"),
        username="artist_user",
        first_name="abdelaleem",
        last_name="ahmed",
        is_male="True",
        is_artist="True",
        is_premium="True"
    ),
]

subscription_plans = [
    SubscriptionPlan(
        name="Individual Plan",
        price="49.99",
        description="EGP 49.99/month after offer period, 1 account - Ad-free music listening - Play anywhere - even offline - Play songs in any order",
        duration=1
    ),
    SubscriptionPlan(
        name="Duo",
        price="64.99",
        description="EGP 64.99/month after offer period, 2 accounts - 2 Premium accounts for a couple under one roof - Ad-free music listening, play offline, play songs in any order",
        duration=1
    ),
    SubscriptionPlan(
        name="Family",
        price="79.99",
        description="EGP 79.99/month after offer period, up to 6 accounts - 6 Premium accounts for family members living under one roof - Block explicit music - Ad-free music listening, play offline, play songs in any order",
        duration=1
    ),
]

categories = [
    Category(
        name='Pop'
    ),
    Category(
        name='Rock'
    ),
    Category(
        name='Hip-Hop'
    ),
    Category(
        name='Sleep'
    )
]


class Command(BaseCommand):
    help = 'Populates the database with Users, Artist, Playlist_categories and SubscriptionPlans ......'
    successfull = "the database has been populated successfully."
    failure = "error occurred while populating the database"

    @transaction.atomic()
    def handle(self, *args, **options):
        print(self.help)
        try:
            User.objects.bulk_create(users)
            SubscriptionPlan.objects.bulk_create(subscription_plans)
            Category.objects.bulk_create(categories)
            user = User.objects.get(email="artist@example.com")
            Artist.objects.create(user=user, bio="new artist")

            premium_user = User.objects.get(email="premium_user@example.com")
            User_SubscriptionPlan.objects.create(user=premium_user, plan_id=1)
            print(self.successfull)
        except:
            raise ValueError(self.failure)
