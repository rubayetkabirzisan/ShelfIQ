from django.core.management.base import BaseCommand
from outlets.models import Outlet


class Command(BaseCommand):
    help = 'Seeds the database with the 3 default Dhaka retail outlets'

    def handle(self, *args, **options):
        outlets = [
            {
                'name': 'ShelfIQ - Gulshan Outlet',
                'address': 'Road 11, Gulshan-1, Dhaka 1212',
                'latitude':  23.7806,
                'longitude': 90.4193,
                'target_posm': 'Foodie Noodles Olympics Display',
            },
            {
                'name': 'ShelfIQ - Banani Outlet',
                'address': 'Road 17, Banani, Dhaka 1213',
                'latitude':  23.7937,
                'longitude': 90.4066,
                'target_posm': 'Foodie Noodles Olympics Display',
            },
            {
                'name': 'ShelfIQ - Dhanmondi Outlet',
                'address': 'Road 27, Dhanmondi, Dhaka 1209',
                'latitude':  23.7461,
                'longitude': 90.3742,
                'target_posm': 'Foodie Noodles Olympics Display',
            },
        ]

        for data in outlets:
            obj, created = Outlet.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            # get_or_create: if the outlet already exists (by name), skip it.
            # If it doesn't exist, create it with the 'defaults' values.
            # Returns (object, created_boolean)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Created: {obj.name}'))
            else:
                self.stdout.write(f'  Already exists: {obj.name}')

        self.stdout.write(self.style.SUCCESS('Outlet seeding complete.'))