from django.test import TestCase

from core.models import User


class UserTests(TestCase):

    def test_user_creation_successful(self):
        test_password = 's0-com3_on!'
        test_user: User = User.objects.create_user(
            username='uprising.muse',
            email='uprising@muse.mu',
            password=test_password,
            first_name='They will',
            last_name='not force us!',
            is_staff=True,
            is_superuser=True
        )

        # Test overall fields
        self.assertTrue(test_user.check_password(test_password), "Password check")
        self.assertEqual(test_user.get_full_name(), "They will not force us!",
                         "Name check")
        self.assertIsNotNone(test_user.get_username(), "Username present")
        self.assertEqual(test_user.username, test_user.get_username(),
                         "Check username field")
        self.assertIsNotNone(test_user.email, "Email present")

        # Retrieval
        retrieved_user = User.objects.get(username='uprising.muse')
        self.assertEqual(retrieved_user, test_user, 'Check retrieved user')
        self.assertTrue(retrieved_user.check_password(test_password),
                        "Retrieved user password check")

    def test_user_creation_normalization(self):
        pass

    def test_user_creation_failure(self):
        pass
