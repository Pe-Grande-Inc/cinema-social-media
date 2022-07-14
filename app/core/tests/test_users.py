from django.test import TestCase
from django.core.exceptions import ValidationError

from core.models import User


class UserTests(TestCase):
    user_kwargs = {
        'username': 'uprising.muse',
        'email': 'uprising@muse.mu',
        'password': 's0-com3_on!',
        'first_name': 'They will',
        'last_name': 'not force us!',
        'is_staff': True,
        'is_superuser': True
    }

    def test_user_creation_successful(self):
        test_user: User = User.objects.create_user(
            **self.user_kwargs
        )

        # Test overall fields
        self.assertTrue(test_user.check_password(self.user_kwargs['password']),
                        "Password check")
        self.assertEqual(test_user.get_full_name(), "They will not force us!",
                         "Name check")
        self.assertIsNotNone(test_user.get_username(), "Username present")
        self.assertEqual(test_user.username, test_user.get_username(),
                         "Check username field")
        self.assertIsNotNone(test_user.email, "Email present")

        # Retrieval
        retrieved_user = User.objects.get(username='uprising.muse')
        self.assertEqual(retrieved_user, test_user, 'Check retrieved user')
        self.assertTrue(retrieved_user.check_password(self.user_kwargs['password']),
                        "Retrieved user password check")

    def test_user_creation_normalization(self):
        email = ' uprising@MUSe.mU   '
        test_user: User = User.objects.create_user(
            **{**self.user_kwargs, 'email': email})
        self.assertEqual(self.user_kwargs['email'], test_user.email,
                         "Check email normalization")

    def test_user_creation_failure(self):
        # Check for e-mail
        with self.assertRaises(ValidationError):
            user_payload = {
                **self.user_kwargs,
            }
            del user_payload['email']
            User.objects.create_user(**user_payload)

        # Check for first_name
        with self.assertRaises(ValidationError):
            user_payload = {
                **self.user_kwargs,
            }
            del user_payload['first_name']
            User.objects.create_user(**user_payload)

        # Check for last_name
        with self.assertRaises(ValidationError):
            user_payload = {
                **self.user_kwargs,
            }
            del user_payload['last_name']
            User.objects.create_user(**user_payload)

        # Check for username
        with self.assertRaises(ValidationError):
            user_payload = {
                **self.user_kwargs,
            }
            del user_payload['username']
            User.objects.create_user(**user_payload)

        # Check for weak password
        with self.assertRaises(ValidationError):
            user_payload = {
                **self.user_kwargs,
                'password': 'pato'
            }
            User.objects.create_user(**user_payload)

        # Check for invalid username
        with self.assertRaises(ValidationError):
            user_payload = {
                **self.user_kwargs,
                'username': 'Mús3'
            }
            User.objects.create_user(**user_payload)
