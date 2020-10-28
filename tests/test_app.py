import unittest

from app import app


class TestApp(unittest.TestCase):
    '''
    Unit testing class for app.py

    Designed to primarily test the routing and collections for our Flask App
    '''

    def __init__(self, *args, **kwargs):
        self.models = ['player', 'team', 'match']

        player_ids = [521, 278]
        team_ids = [173, 80]
        match_ids = [589000, 591151]

        self.ids = {'player': player_ids, 'team': team_ids, 'match': match_ids}

        super(TestApp, self).__init__(*args, **kwargs)

    def setUp(self):
        ''' Set flask to testing mode prior to each test '''
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def test_index(self):
        ''' Test that the index route returns code 200 '''
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        ''' Test that the index route returns code 200 '''
        response = self.app.get('/about', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_model(self):
        '''
        Test the various model routes

        /model/{player, team, match} should return 200
        /model/{anything else} and /model/<> should 404
        '''

        # These are the valid models and should return a code 200
        for model in self.models:
            response = self.app.get(f'/model/{model}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

        # These are examples of invalid models and should 404
        for model in ['this_should_fail', 'players', '']:
            response = self.app.get(f'/model/{model}', follow_redirects=True)
            self.assertEqual(response.status_code, 404)

    def test_instance(self):
        '''
        Test the various instance routes

        /instance/{player, team, match}/<valid id> should return 200
        /instance/{player, team, match}/<invalid id>,
            /instance/{anything else}, /instance/<> should 404
        '''

        # These are combinations of valid models and ids
        for model, ids in self.ids.items():
            for id in ids:
                response = self.app.get(f'/instance/{model}/{id}', follow_redirects=True)
                self.assertEqual(response.status_code, 200)

        # These are examples of valid models but invalid ids
        for model in self.ids:
            for id in [123412341234, 'asdf', 0, 'model', 'player']:
                response = self.app.get(f'/instance/{model}/{id}', follow_redirects=True)
                self.assertEqual(response.status_code, 404)

        # These are examples of invalid models
        for model in ['this_should_fail', 'players', '']:
            # Valid IDs but they should still 404 since these aren't real models
            for ids in self.ids.values():
                for id in ids:
                    response = self.app.get(f'/instance/{model}/{id}', follow_redirects=True)
                    self.assertEqual(response.status_code, 404)

            # Invalid IDs
            for id in [123412341234, 'asdf', 0, 'model', 'player']:
                response = self.app.get(f'/instance/{model}/{id}', follow_redirects=True)
                self.assertEqual(response.status_code, 404)
