from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, Transaction

class MemberDatabaseIntegrationTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        # Create a profile if it doesn't exist, with the specified address
        self.profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={'address': "123 Test St."}
        )
        # If the profile was created, it's fine. If it already exists, update the address for testing.
        if not created:
            self.profile.address = "123 Test St."
            self.profile.save()
    
    def test_profile_creation(self):
        # Test that profile is correctly linked to the user
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.address, '123 Test St.')

    def test_transaction_creation(self):
        # Test that transactions are correctly associated with the user
        transaction = Transaction.objects.create(user=self.user, amount=100, description="Test transaction")
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.description, "Test transaction")
        self.assertEqual(transaction.user.username, 'testuser')
