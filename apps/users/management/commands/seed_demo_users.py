from django.core.management.base import BaseCommand
from django.db import models
from apps.users.models import User, University, Organization, StudentProfile, FacultyProfile, DemoCredential

class Command(BaseCommand):
    help = "Seed or update the 6 required demo user accounts idempotently, and remove any Master Admin account."

    def handle(self, *args, **options):
        self.stdout.write("Starting idempotent demo user seeding...")

        # 1. Delete existing Master Admin demo account(s)
        deleted_count, _ = User.objects.filter(
            models.Q(role='admin') |
            models.Q(email__in=['superadmin@confluence.gov.in', 'masteradmin@confluence.demo', 'admin@confluence.demo'])
        ).delete()
        if deleted_count > 0:
            self.stdout.write(self.style.WARNING(f"Removed {deleted_count} Master Admin account(s) from database."))

        # 2. Ensure primary demo University and Organization exist
        bit, _ = University.objects.get_or_create(
            name="Birsa Institute of Technology (BIT) Sindri",
            defaults={"code": "BITS-DHN", "district": "Dhanbad"}
        )

        tata, _ = Organization.objects.get_or_create(
            name="Tata Steel Foundation & CSR",
            defaults={"org_type": "csr", "website": "https://www.tatasteel.com"}
        )

        # 3. Define the 6 demo users configuration exactly as required
        demo_users_data = [
            {
                "email": "citizen@confluence.demo",
                "password": "Citizen@123",
                "role": User.Role.CITIZEN,
                "role_name": "Citizen",
                "name": "Citizen User",
                "is_staff": False,
                "is_superuser": False,
                "university": None,
                "organization": None,
                "description": "Public citizen role to report societal problems and participate in discussions.",
            },
            {
                "email": "student@confluence.demo",
                "password": "Student@123",
                "role": User.Role.STUDENT,
                "role_name": "Student",
                "name": "Student Innovator",
                "is_staff": False,
                "is_superuser": False,
                "university": bit,
                "organization": None,
                "description": "Student innovator role to submit technical pitches and work on adopted projects.",
            },
            {
                "email": "coordinator@confluence.demo",
                "password": "Coordinator@123",
                "role": User.Role.UNIVERSITY_COORDINATOR,
                "role_name": "Coordinator",
                "name": "University Coordinator",
                "is_staff": False,
                "is_superuser": False,
                "university": bit,
                "organization": None,
                "description": "University coordinator to adopt challenges, validate pitches, and manage campus teams.",
            },
            {
                "email": "mentor@confluence.demo",
                "password": "Mentor@123",
                "role": User.Role.FACULTY_MENTOR,
                "role_name": "Mentor",
                "name": "Faculty Mentor",
                "is_staff": False,
                "is_superuser": False,
                "university": bit,
                "organization": None,
                "description": "Faculty mentor to guide student technical proposals and evaluate milestones.",
            },
            {
                "email": "govtadmin@confluence.demo",
                "password": "GovtAdmin@123",
                "role": User.Role.GOV_ADMIN,
                "role_name": "Govt Admin",
                "name": "Govt Admin",
                "is_staff": True,
                "is_superuser": False,
                "university": None,
                "organization": None,
                "description": "Government admin officer oversight dashboard for state-wide issues & analytics.",
            },
            {
                "email": "industry@confluence.demo",
                "password": "Industry@123",
                "role": User.Role.INDUSTRY_PARTNER,
                "role_name": "Industry",
                "name": "Industry Partner",
                "is_staff": False,
                "is_superuser": False,
                "university": None,
                "organization": tata,
                "description": "Industry partner and CSR representative for funding, sponsorship, and mentorship.",
            },
        ]

        # Clean DemoCredential table of any old entries
        DemoCredential.objects.all().delete()

        created_users = []
        for u_data in demo_users_data:
            email = u_data["email"]
            pwd = u_data["password"]

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": u_data["name"],
                    "role": u_data["role"],
                    "is_staff": u_data["is_staff"],
                    "is_superuser": u_data["is_superuser"],
                    "university": u_data["university"],
                    "organization": u_data["organization"],
                }
            )

            # Update credentials & attributes to guarantee idempotency and exact specs
            user.name = u_data["name"]
            user.role = u_data["role"]
            user.is_staff = u_data["is_staff"]
            user.is_superuser = False  # Explicitly ensure false for all demo accounts
            user.university = u_data["university"]
            user.organization = u_data["organization"]
            user.set_password(pwd)
            user.save()

            # Seed DemoCredential table row for Supabase dashboard viewing
            DemoCredential.objects.create(
                role_name=u_data["role_name"],
                email=email,
                password=pwd,
                role_code=u_data["role"],
                is_staff=u_data["is_staff"],
                description=u_data["description"]
            )

            # Create profiles if needed
            if user.role == User.Role.STUDENT:
                StudentProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "university": bit,
                        "department": "Computer Science & Engineering",
                        "roll_no": "2024-CSE-001",
                        "year_of_study": 3,
                    }
                )
            elif user.role == User.Role.FACULTY_MENTOR:
                FacultyProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "university": bit,
                        "designation": "Associate Professor",
                        "department": "Civil & Environmental Engineering",
                    }
                )

            status_str = "Created" if created else "Updated"
            created_users.append(f" - {user.role} ({user.email}): {status_str}")

        self.stdout.write(self.style.SUCCESS("Successfully seeded 6 demo accounts and populated DemoCredential table:"))
        for info in created_users:
            self.stdout.write(self.style.SUCCESS(info))

