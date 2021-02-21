from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# when a user is saved, then send a signal and this signal will be received by this receiver
# this receiver will then run the create_profile function which takes the arguments this post_save passewd to it
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # if the user was created create a profile object, where the user is equal to the instance the user was created
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
