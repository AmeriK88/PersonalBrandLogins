from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .admin import CareerProfileAdmin, ExperienceAdmin
from .models import CareerProfile, Experience


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class CareerOverviewTests(TestCase):
    def setUp(self):
        self.profile = CareerProfile.objects.get(pk=1)

    def test_overview_renders_experiences_in_chronological_sections(self):
        Experience.objects.create(
            category="high_school",
            team="Sodus Spartans",
            years="2004–2005",
            start_year=2004,
        )
        Experience.objects.create(
            category="college",
            team="Canisius Golden Griffins",
            years="2007–2011",
            start_year=2007,
        )
        Experience.objects.create(
            category="professional",
            team="Later Club",
            years="2014–2015",
            start_year=2014,
        )
        Experience.objects.create(
            category="professional",
            team="First Club",
            years="2011–2012",
            start_year=2011,
        )

        response = self.client.get(reverse("career:overview"))

        self.assertEqual(response.status_code, 200)
        page = response.content.decode()
        self.assertLess(page.index("Sodus Spartans"), page.index("Canisius Golden Griffins"))
        self.assertLess(page.index("First Club"), page.index("Later Club"))
        self.assertContains(response, "THE")
        self.assertContains(response, "JOURNEY")

    def test_professional_records_without_optional_details_render(self):
        Experience.objects.create(
            category="professional",
            team="A Team Without Optional Details",
            years="Unknown season",
        )

        response = self.client.get(reverse("career:overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A Team Without Optional Details")
        self.assertNotContains(response, "No professional experience records")

    def test_missing_profile_uses_supplied_defaults(self):
        CareerProfile.objects.filter(pk=1).delete()

        response = self.client.get(reverse("career:overview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gregory Mark Logins Jr.")
        self.assertContains(response, "13")
        self.assertContains(response, "9,750")
        self.assertContains(response, "Canisius College")

    def test_profile_statistics_and_quick_facts_are_rendered(self):
        self.profile.games = 401
        self.profile.minutes = 10125
        self.profile.full_name = "A Profile Name"
        self.profile.current_role = "Teacher and mentor"
        self.profile.save()

        response = self.client.get(reverse("career:overview"))

        self.assertContains(response, "401")
        self.assertContains(response, "10,125")
        self.assertContains(response, "A Profile Name")
        self.assertContains(response, "Teacher and mentor")
        self.assertContains(response, "Career figures supplied for this profile.")


class CareerModelAndAdminTests(TestCase):
    def test_experiences_are_ordered_by_start_year_with_unknown_dates_last(self):
        newest = Experience.objects.create(
            category="professional",
            team="Newest",
            years="2015–2016",
            start_year=2015,
        )
        undated = Experience.objects.create(
            category="professional",
            team="Undated",
            years="Unclear",
        )
        oldest = Experience.objects.create(
            category="professional",
            team="Oldest",
            years="2011–2012",
            start_year=2011,
        )

        self.assertEqual(
            list(Experience.objects.all()),
            [oldest, newest, undated],
        )

    def test_start_year_validation_rejects_non_year_values(self):
        experience = Experience(
            category="professional",
            team="Invalid date",
            years="999",
            start_year=999,
        )

        with self.assertRaises(ValidationError):
            experience.full_clean()

    def test_career_profile_save_enforces_singleton_primary_key(self):
        original = CareerProfile.objects.get(pk=1)
        replacement = CareerProfile(full_name="Updated profile")
        replacement.save()

        self.assertEqual(CareerProfile.objects.count(), 1)
        self.assertEqual(CareerProfile.objects.get(pk=1).full_name, "Updated profile")
        self.assertEqual(original.pk, 1)

    def test_admin_keeps_singleton_managed_and_image_action_available(self):
        request = RequestFactory().get("/admin/career/careerprofile/")
        profile_admin = CareerProfileAdmin(CareerProfile, admin.site)
        experience_admin = ExperienceAdmin(Experience, admin.site)

        self.assertFalse(profile_admin.has_add_permission(request))
        self.assertFalse(profile_admin.has_delete_permission(request))
        self.assertIn("clear_image", experience_admin.actions)
        self.assertIn(CareerProfile, admin.site._registry)
        self.assertIn(Experience, admin.site._registry)
