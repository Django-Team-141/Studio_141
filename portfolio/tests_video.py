import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from portfolio.models import Project, validate_video_content, validate_video_size

MP4 = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00" + b"x" * 200
WEBM = b"\x1a\x45\xdf\xa3" + b"x" * 200


def make_project(**extra):
    data = dict(
        title="My Project", slug="my-project",
        desc_fa="توضیح کوتاه", desc_en="A short description", accent="green",
    )
    data.update(extra)
    return Project.objects.create(**data)


class TempMediaMixin:
    """فایل‌های آپلودشده در تست داخل یک پوشه‌ی موقت می‌روند، نه پوشه‌ی media پروژه."""

    def setUp(self):
        super().setUp()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        override = override_settings(MEDIA_ROOT=tmp.name)
        override.enable()
        self.addCleanup(override.disable)


class VideoValidationTests(TestCase):
    def test_real_mp4_and_webm_are_accepted(self):
        validate_video_content(SimpleUploadedFile("a.mp4", MP4))
        validate_video_content(SimpleUploadedFile("a.webm", WEBM))

    def test_a_renamed_text_file_is_refused(self):
        fake = SimpleUploadedFile("fake.mp4", b"this is only text, not a video at all")
        with self.assertRaises(ValidationError):
            validate_video_content(fake)

    def test_big_videos_are_refused(self):
        with patch("portfolio.models.MAX_VIDEO_BYTES", 100):
            with self.assertRaises(ValidationError):
                validate_video_size(SimpleUploadedFile("a.mp4", MP4))


class VideoPageTests(TempMediaMixin, TestCase):
    def _with_video(self, **extra):
        return make_project(video=SimpleUploadedFile("demo.mp4", MP4, content_type="video/mp4"), **extra)

    def test_project_page_links_to_the_video_page(self):
        self._with_video()
        r = self.client.get("/fa/work/my-project/")
        self.assertContains(r, 'href="/fa/work/my-project/video/"')

    def test_project_without_video_has_no_video_link_or_page(self):
        make_project()
        r = self.client.get("/fa/work/my-project/")
        self.assertNotContains(r, "/video/")
        self.assertEqual(self.client.get("/fa/work/my-project/video/").status_code, 404)

    def test_video_page_plays_the_file_directly(self):
        project = self._with_video()
        r = self.client.get("/en/work/my-project/video/")
        self.assertContains(r, "<video")
        self.assertContains(r, 'type="video/mp4"')
        self.assertContains(r, project.video.url)

    def test_unpublished_project_video_is_404(self):
        self._with_video(is_published=False)
        self.assertEqual(self.client.get("/fa/work/my-project/video/").status_code, 404)

    def test_home_card_shows_the_video_link(self):
        self._with_video()
        self.assertContains(self.client.get("/en/"), 'href="/en/work/my-project/video/"')

    def test_project_page_shows_the_technologies(self):
        make_project(tags="Django, REST API")
        r = self.client.get("/en/work/my-project/")
        self.assertContains(r, "<em>Django</em>")
        self.assertContains(r, "<em>REST API</em>")


class FileCleanupTests(TempMediaMixin, TestCase):
    def test_files_are_deleted_with_the_project(self):
        project = make_project(video=SimpleUploadedFile("demo.mp4", MP4))
        path = Path(project.video.path)
        self.assertTrue(path.exists())
        with self.captureOnCommitCallbacks(execute=True):
            project.delete()
        self.assertFalse(path.exists())

    def test_replaced_video_is_removed(self):
        project = make_project(video=SimpleUploadedFile("demo.mp4", MP4))
        old = Path(project.video.path)
        with self.captureOnCommitCallbacks(execute=True):
            project.video = SimpleUploadedFile("new.mp4", MP4)
            project.save()
        self.assertFalse(old.exists())
        self.assertTrue(Path(project.video.path).exists())

    def test_unchanged_video_is_kept(self):
        project = make_project(video=SimpleUploadedFile("demo.mp4", MP4))
        path = Path(project.video.path)
        with self.captureOnCommitCallbacks(execute=True):
            project.title = "Another title"
            project.save()
        self.assertTrue(path.exists())