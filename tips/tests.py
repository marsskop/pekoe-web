from django.test import TestCase
from .models import User, Customer


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="test", first_name="Test", last_name="Testovich", email="user@user.ru")

    def test_customer_creation(self):
        """Customer object should be created for each user"""
        user = User.objects.get(username="test")
        customer = Customer.objects.get(user=user)
        self.assertEqual(user, customer.user)
