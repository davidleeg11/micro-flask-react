# services/sites/project/tests/test_sites.py


import json
import unittest

from project.tests.base import BaseTestCase
from project import db
from project.api.models import Site


def add_site(site):
    site = Site(site=site)
    db.session.add(site)
    db.session.commit()
    return site


class TestSiteService(BaseTestCase):
    """Tests for the sites Service."""

    def test_sites(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/sites/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_site(self):
        """Ensure a new site can be added to the database."""
        with self.client:
            response = self.client.post(
                '/sites',
                data=json.dumps({
                    'site': 'michael',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('michael', data['message'])
            self.assertIn('success', data['status'])

    def test_add_site_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/sites',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_site_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not have a site key.
        """
        with self.client:
            response = self.client.post(
                '/sites',
                data=json.dumps({'email': 'michael'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_site_duplicate_site(self):
        """Ensure error is thrown if the site already exists."""
        with self.client:
            self.client.post(
                '/sites',
                data=json.dumps({
                    'site': 'michael',
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/sites',
                data=json.dumps({
                    'site': 'michael',
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That site already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_site(self):
        """Ensure get single site behaves correctly."""
        site = add_site('michael')
        with self.client:
            response = self.client.get(f'/sites/{site.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('michael', data['data']['site'])
            self.assertIn('success', data['status'])

    def test_all_sites(self):
        """Ensure get CSR Migration 0.5 behaves correctly."""
        add_site('michael')
        add_site('fletcher')
        with self.client:
            response = self.client.get('/sites')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['sites']), 2)
            self.assertIn('michael', data['data']['sites'][0]['site'])
            self.assertIn('fletcher', data['data']['sites'][1]['site'])
            self.assertIn('success', data['status'])

    def test_single_site_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/sites/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Site does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_site_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/sites/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('Site does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_main_no_sites(self):
        """Ensure the main route behaves correctly when no sites have been
        added to the database."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CSR Migration 0.5', response.data)
        self.assertIn(b'<p>No sites!</p>', response.data)

    def test_main_with_sites(self):
        """Ensure the main route behaves correctly when sites have been
        added to the database."""
        add_site('michael')
        add_site('fletcher')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'CSR Migration 0.5', response.data)
            self.assertNotIn(b'<p>No sites!</p>', response.data)
            self.assertIn(b'michael', response.data)
            self.assertIn(b'fletcher', response.data)

    def test_main_add_site(self):
        """Ensure a new site can be added to the database."""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(site='michael'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'CSR Migration 0.5', response.data)
            self.assertNotIn(b'<p>No sites!</p>', response.data)
            self.assertIn(b'michael', response.data)


if __name__ == '__main__':
    unittest.main()
