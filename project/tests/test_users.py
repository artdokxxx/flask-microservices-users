import json
from project.tests.base import BaseTestCase
from project import db
from project.api.models import User


class TestUserServices(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_users(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com'
                )),
                content_type='application/json'
            )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertIn('michael@realpython.com was added', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is throw if the JSON object is empty"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type='application/json'
            )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload', data['message'])
        self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is throw if the JSON object does not have a
        username key."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='michael@realpython.com'
                )),
                content_type='application/json'
            )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload', data['message'])
        self.assertIn('fail', data['status'])

    def test_add_user_dublicate_key(self):
        """Ensure error is throw if the JSON object dublicate request"""
        def send_response():
            return self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='michael@realpython.com',
                    username='michael'
                )),
                content_type='application/json'
            )

        with self.client:
            send_response()
            response = send_response()
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Sorry. That email already exists', data['message'])
        self.assertIn('fail', data['status'])

    def test_get_single_user(self):
        """Ensure get single user behaves correctly."""
        user = User(username='michael', email='michael@realpython.com')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('michael', data['data']['username'])
            self.assertIn('michael@realpython.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is throw if an id is not provided"""
        with self.client:
            response = self.client.get('/users/sdfs')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist', data['message'])

    def test_single_user_incorrect_id(self):
        """Ensure error is throw if an id does not exist"""
        with self.client:
            response = self.client.get('/users/9999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist', data['message'])

    def test_get_users(self):
        """Ensure get all users behaves correctly."""

        def add_user(username, email):
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            return user

        add_user('michael', 'michael@realpython.com')
        add_user('jesica', 'jesica@realpython.com')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertTrue('created_at' in data['data']['users'][0])
            self.assertTrue('created_at' in data['data']['users'][1])

            self.assertIn('michael', data['data']['users'][0]['username'])
            self.assertIn('michael@realpython.com',
                          data['data']['users'][0]['email'])

            self.assertIn('jesica', data['data']['users'][1]['username'])
            self.assertIn('jesica@realpython.com',
                          data['data']['users'][1]['email'])

            self.assertIn('success', data['status'])

    def test_index_no_users(self):
        """Ensure the main route behaves correctly when no users have been
        added to the database."""
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<h1>All Users</h1>', response.data)
            self.assertIn(b'<p>No users!</p>', response.data)

    def test_index_2_users(self):
        """Ensure the main route behaves correctly when 2 users in database."""

        def add_user(username, email):
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
            return user

        add_user('test1', '1@1.com')
        add_user('test2', '2@2.com')

        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<h1>All Users</h1>', response.data)
            self.assertNotIn(b'<strong>No users!</strong>', response.data)
            self.assertIn(b'<strong>test1</strong>', response.data)
            self.assertIn(b'<strong>test2</strong>', response.data)

    def test_index_add_users(self):
        """Ensure a new user can be added to the database."""

        with self.client:
            response = self.client.post('/', follow_redirects=True, data={
                'username': 'test2',
                'email': '2@2.com'
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<h1>All Users</h1>', response.data)
            self.assertNotIn(b'<strong>No users!</strong>', response.data)
            self.assertIn(b'<strong>test2</strong>', response.data)
