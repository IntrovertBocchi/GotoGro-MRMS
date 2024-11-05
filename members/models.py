from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, Avg

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

    # Preferences field stored as char field
    preferences = models.CharField(max_length=100, blank=True)

    # Postcode field
    postcode = models.CharField(max_length=10, blank=True)

    # Suburb field
    suburb = models.CharField(max_length=50, blank=True)

    # City field
    city = models.CharField(max_length=50, blank=True)

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

    # Price per unit
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Total cost of purchase
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Time of purchase
    purchase_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        #Calculate total price before saving
        self.total_price = self.purchase_quantity * self.price_per_unit
        super().save(*args, **kwargs)
        
        
    def __str__(self):
        return f"{self.member.username} - {self.item_name} ({self.purchase_quantity})"



class Inventory(models.Model):
    
    item_name = models.CharField(max_length=255, unique=True)
    inventory_amount = models.IntegerField(default=1000)
    remaining_quantity = models.IntegerField(default=0)
    recommended_inventory_levels = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.item_name} - Inventory: {self.inventory_amount}, Remaining: {self.remaining_quantity}"

    def calculate_remaining_quantity(self):

        # Calculate the total purchase quantity from related sales
        total_purchase_quantity = Sale.objects.filter(item_name=self.item_name).aggregate(
            total=models.Sum('purchase_quantity')
        )['total'] or 0

        # Calculate remaining quantity
        self.remaining_quantity = self.inventory_amount - total_purchase_quantity

    def calculate_recommended_level(self):
        
        # Calculate average sales for item
        avg_sales = Sale.objects.filter(item_name=self.item_name).aggregate(
            Avg('purchase_quantity')
        )['purchase_quantity__avg'] or 0
        
        # Set recommended level as twice the average sale quantity
        self.recommended_inventory_levels = int(avg_sales * 2) if avg_sales else 100

    def save(self, *args, **kwargs):

        # Update remaining quantity and recommended levels before saving
        self.calculate_remaining_quantity()
        self.calculate_recommended_level()
        super().save(*args, **kwargs)
    

class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('high_purchase_quantity', 'High Purchase Quantity'),
        ('high_sales_amount', 'High Sales Amount'),
        ('low_inventory', 'Low Inventory')
    ]

    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.message[:50]}"
    
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Sale)
def create_or_update_inventory(sender, instance, **kwargs):

    # Get or create the Inventory object based on the sale's item_name
    inventory, created = Inventory.objects.get_or_create(item_name=instance.item_name)

    # Save the inventory to trigger remaining quantity calculation
    inventory.save()

