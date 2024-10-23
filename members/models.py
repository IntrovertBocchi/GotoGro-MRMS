from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Models to store the information for each user
class Profile(models.Model):

    # One-to-one relationship with the user model, deleting the user will also delete user profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # First name of user, cannot be blank
    first_name = models.CharField(max_length=30, blank=False)

    # Last name of user, cannot be blank
    last_name = models.CharField(max_length=30, blank=False)

    # Address field for user profile, cannot be left blank
    address = models.TextField(max_length=255, blank=True)

    # Phone number for user profile, cannot be left blank
    phone_number = models.CharField(max_length=15, blank=True)

    # Preferences field stored as JSON, cannot be left blank with default of an empty dictionary
    # Dict ensures that each profile gets a new, separate dictionary
    preferences = models.CharField(max_length=100, blank=True)

    # String representing profile model, displays the username
    def __str__(self): 
        return f"{self.user.username}'s profile"

# Model for storing user transactions
class Transaction(models.Model):

    # ForeignKey relationship with user model, deleting user will also delete the user's transactions
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Automatic setting of date and time when transaction is made
    date = models.DateTimeField(auto_now_add=True)

    # Decimal field for transaction amount, allows 10 digits with 2 decimal places
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Short description for transaction
    description = models.CharField(max_length=255)

    # String representing transaction model, shows username, amount, and date
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"

class Sale(models.Model):

    # Link to member
    member = models.ForeignKey(User, on_delete=models.CASCADE)

    # Name of purchased item
    item_name = models.CharField(max_length=255)

    # Number of items purchased
    purchase_quantity = models.IntegerField(default=1)

    # Total cost of purchase
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Time of purchase
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.username} - {self.item_name} ({self.quantity})"




@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

