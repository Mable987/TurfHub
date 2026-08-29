from django.conf import settings
from django.db import models

# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    avatar_preset = models.CharField(max_length=20, null=True, blank=True)

    AVATAR_PRESETS = [f"avatar{i}.svg" for i in range(1, 9)]

    @property
    def avatar_url(self):
        """Custom upload wins; otherwise a chosen preset; otherwise None (initials fallback)."""
        if self.avatar:
            return self.avatar.url
        if self.avatar_preset in self.AVATAR_PRESETS:
            from django.templatetags.static import static
            return static(f"avatars/{self.avatar_preset}")
        return None

    def __str__(self):
        return f"{self.user.username}'s profile"
