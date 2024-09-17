from django.core.management import BaseCommand
from user.models import User, Department


class Command(BaseCommand):
    help = "Seeds an admin user into the database"

    def handle(self, *args, **kwargs):
        email = "admin@gmail.com"
        password = "Password1."

        # Check if the user already exists
        if not User.objects.filter(email=email).exists():
            # Create the superuser
            User.objects.create_superuser(
                firstname="Admin",
                lastname="User",
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully created superuser with email {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser with email {email} already exists"))

        departments = [
            {
                'name': "Agriculture",
                'code': "AGRI"
            },
            {
                'name': "Computer Science",
                'code': "CSCI"
            },
            {
                'name': "Electrical Engineering",
                'code': "EE"
            },
            {
                'name': "Mechanical Engineering",
                'code': "MECH"
            },
            {
                'name': "Civil Engineering",
                'code': "CE"
            },
            {
                'name': "Business Administration",
                'code': "BA"
            },
            {
                'name': "Mathematics",
                'code': "MATH"
            },
            {
                'name': "Physics",
                'code': "PHYS"
            }
        ]
        department_list = []
        for dept in departments:
            department_list.append(Department(**dept))

        Department.objects.bulk_create(department_list)
