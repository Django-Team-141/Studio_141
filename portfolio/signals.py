from django.db import transaction
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Project, ProjectImage

# فایل‌هایی که هر مدل دارد
FILE_FIELDS = {
    Project: ("image", "video", "video_poster"),
    ProjectImage: ("image",),
}


def _delete_after_commit(field_file):
    """فایل را بعد از ذخیره‌ی موفق دیتابیس پاک می‌کند، تا اگر چیزی خراب شد فایل از دست نرود."""
    if not field_file or not field_file.name:
        return
    storage, name = field_file.storage, field_file.name
    transaction.on_commit(lambda: storage.delete(name))


@receiver(pre_save, sender=Project)
@receiver(pre_save, sender=ProjectImage)
def drop_replaced_files(sender, instance, **kwargs):
    # اگر فایل عوض یا خالی شد، فایل قبلی پاک می‌شود
    if not instance.pk:
        return
    old = sender.objects.filter(pk=instance.pk).first()
    if not old:
        return
    for name in FILE_FIELDS[sender]:
        before = getattr(old, name)
        after = getattr(instance, name)
        if before and before.name != (after.name or ""):
            _delete_after_commit(before)


@receiver(post_delete, sender=Project)
@receiver(post_delete, sender=ProjectImage)
def drop_deleted_files(sender, instance, **kwargs):
    for name in FILE_FIELDS[sender]:
        _delete_after_commit(getattr(instance, name))