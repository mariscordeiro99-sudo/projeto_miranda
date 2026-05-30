from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Attachment, Profile, VisualIdentity


def delete_file(file_field):
    if file_field and file_field.name:
        file_field.delete(save=False)


def previous_file(instance, field_name):
    if not instance.pk:
        return None

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return None

    return getattr(old_instance, field_name)


def delete_replaced_file(instance, field_name):
    old_file = previous_file(instance, field_name)
    new_file = getattr(instance, field_name)

    if old_file and old_file.name and old_file.name != getattr(new_file, 'name', ''):
        delete_file(old_file)


@receiver(pre_save, sender=Profile)
def delete_replaced_profile_picture(sender, instance, **kwargs):
    delete_replaced_file(instance, 'profile_picture')


@receiver(pre_save, sender=VisualIdentity)
def delete_replaced_visual_identity_files(sender, instance, **kwargs):
    delete_replaced_file(instance, 'logo')
    delete_replaced_file(instance, 'coat_of_arms')


@receiver(pre_save, sender=Attachment)
def delete_replaced_attachment_file(sender, instance, **kwargs):
    delete_replaced_file(instance, 'file')


@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    delete_file(instance.profile_picture)


@receiver(post_delete, sender=VisualIdentity)
def delete_visual_identity_files(sender, instance, **kwargs):
    delete_file(instance.logo)
    delete_file(instance.coat_of_arms)


@receiver(post_delete, sender=Attachment)
def delete_attachment_file(sender, instance, **kwargs):
    delete_file(instance.file)
