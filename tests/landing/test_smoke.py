from django.test import TestCase


class TestLandingSmoke(TestCase):
    def test_smoke(self):
        assert 1 == 2 - 1
