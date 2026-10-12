from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from portfolio.models import Project, validate_image_size


def make_project(**extra):
    data = dict(
        title="My Project", slug="my-project",
        desc_fa="توضیح کوتاه", desc_en="A short description", accent="green",
    )
    data.update(extra)
    return Project.objects.create(**data)


class ProjectPageTests(TestCase):
    def test_detail_page_in_both_languages(self):
        make_project()
        fa = self.client.get("/fa/work/my-project/")
        en = self.client.get("/en/work/my-project/")
        self.assertContains(fa, "My Project")
        self.assertContains(fa, "توضیح کوتاه")
        self.assertContains(en, "A short description")

    def test_unpublished_and_unknown_projects_are_404(self):
        make_project(slug="hidden", is_published=False)
        self.assertEqual(self.client.get("/fa/work/hidden/").status_code, 404)
        self.assertEqual(self.client.get("/fa/work/nope/").status_code, 404)

    def test_home_card_links_to_the_detail_page(self):
        make_project()
        self.assertContains(self.client.get("/en/"), 'href="/en/work/my-project/"')

    def test_sitemap_has_published_projects_only(self):
        make_project()
        make_project(slug="hidden", title="Hidden", is_published=False)
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("http://testserver/fa/work/my-project/", body)
        self.assertNotIn("/work/hidden/", body)


class ProjectValidationTests(TestCase):
    def test_only_web_links_are_accepted(self):
        p = Project(
            title="x", slug="x", desc_fa="a", desc_en="b",
            demo_url="javascript:alert(1)",
        )
        with self.assertRaises(ValidationError):
            p.full_clean()
        p.demo_url = "https://example.com"
        p.full_clean()  # حالا خطا نمی‌دهد

    def test_images_over_two_megabytes_are_refused(self):
        too_big = SimpleUploadedFile("big.png", b"x" * (2 * 1024 * 1024 + 1))
        with self.assertRaises(ValidationError):
            validate_image_size(too_big)
        fine = SimpleUploadedFile("ok.png", b"x" * (2 * 1024 * 1024))
        validate_image_size(fine)