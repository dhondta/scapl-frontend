from django.test import TestCase
from .models import GenericUser

"""
A generic user model is defined with the following characteristics:
 - The main field is the email
 - A new instance is created as inactive and without staff responsibility (that is, the user has no access to the admin site)
 - All other fields are optional
"""


class GenericUserTests(TestCase):
    """ This test class checks some user properties according to the defined user policy """
    def test_user_responsibilities(self):
        new_user = GenericUser(email='testuser@localhost')
        self.assertEqual(new_user.is_active, False)
        self.assertEqual(new_user.is_staff, False)
        self.assertEqual(new_user.is_superuser, False)
