import unittest

from app import app
from app import get_players, get_matches, get_teams


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
                response = self.app.get(
                    f'/instance/{model}/{id}', follow_redirects=True)
                self.assertEqual(response.status_code, 200)

        # These are examples of valid models but invalid ids
        for model in self.ids:
            for id in [123412341234, 'asdf', 0, 'model', 'player']:
                response = self.app.get(
                    f'/instance/{model}/{id}', follow_redirects=True)
                self.assertEqual(response.status_code, 404)

        # These are examples of invalid models
        for model in ['this_should_fail', 'players', '']:
            # Valid IDs but they should still 404 since these aren't real models
            for ids in self.ids.values():
                for id in ids:
                    response = self.app.get(
                        f'/instance/{model}/{id}', follow_redirects=True)
                    self.assertEqual(response.status_code, 404)

            # Invalid IDs
            for id in [123412341234, 'asdf', 0, 'model', 'player']:
                response = self.app.get(
                    f'/instance/{model}/{id}', follow_redirects=True)
                self.assertEqual(response.status_code, 404)

    def test_sort_players(self):
        '''
        Test sorting of players by a numeric key.
        '''
        # Forward sort
        players = get_players(offset=0, per_page=1000,
                              sort_by='goals', search_query=None)[0]
        goals = -1
        for player in players:
            self.assertTrue(player.goals >= goals)
            goals = player.goals

        # Backward sort
        players = get_players(offset=0, per_page=1000,
                              sort_by='-goals', search_query=None)[0]
        goals = 10000
        for player in players:
            self.assertTrue(player.goals <= goals)
            goals = player.goals

    def test_sort_teams(self):
        '''
        Test sorting of teams by a string key.
        '''
        # Forward sort
        teams = get_teams(offset=0, per_page=1000,
                          sort_by='name', search_query=None)[0]
        name = "A"
        for team in teams:
            self.assertTrue(team.name >= name)
            name = team.name

        # Backward sort
        teams = get_teams(offset=0, per_page=1000,
                          sort_by='-name', search_query=None)[0]
        name = "z"
        for team in teams:
            self.assertTrue(team.name <= name)
            name = team.name

    def test_sort_matches(self):
        '''
        Test sorting of matches by a date key.
        '''
        # Forward sort
        matches = get_matches(offset=0, per_page=1000,
                              sort_by='date', search_query=None)[0]
        date = matches[0].date
        for match in matches:
            self.assertTrue(match.date >= date)
            date = match.date

        # Backward sort
        matches = get_matches(offset=0, per_page=1000,
                              sort_by='-date', search_query=None)[0]
        date = matches[0].date
        for match in matches:
            self.assertTrue(match.date <= date)
            date = match.date

    def test_search_player_name(self):
        '''
        Test searching of players by name

        We need to make sure that searching works AND that it still works with sorting
        '''
        # TODO: Make sure that it works with filtering as well

        # Searching for a part of a player name with forward sort
        query = 'Diego'
        players = get_players(offset=0, per_page=1000,
                              sort_by='goals', search_query=query)[0]

        goals = -1
        for player in players:
            self.assertTrue(player.goals >= goals)
            self.assertTrue(query in player.name
                            or query in player.position
                            or query in player.team_name)
            goals = player.goals

        # Searching for a part of a player name with backward sort
        players = get_players(offset=0, per_page=1000,
                              sort_by='-goals', search_query=query)[0]

        goals = 10000
        for player in players:
            self.assertTrue(player.goals <= goals)
            self.assertTrue(query in player.name
                            or query in player.position
                            or query in player.team_name)
            goals = player.goals

    def test_search_player_position(self):
        '''
        Test searching of players by position

        We need to make sure that searching works AND that it still works with sorting
        '''
        # TODO: Make sure that it works with filtering as well

        # Searching for a part of a player position with forward sort
        query = 'M'
        players = get_players(offset=0, per_page=1000,
                              sort_by='goals', search_query=query)[0]

        goals = -1
        for player in players:
            self.assertTrue(player.goals >= goals)
            self.assertTrue(query in player.name
                            or query in player.position
                            or query in player.team_name)
            goals = player.goals

        # Searching for a part of a player position with backward sort
        players = get_players(offset=0, per_page=1000,
                              sort_by='-goals', search_query=query)[0]

        goals = 10000
        for player in players:
            self.assertTrue(player.goals <= goals)
            self.assertTrue(query in player.name
                            or query in player.position
                            or query in player.team_name)
            goals = player.goals

    def test_search_player_team_name(self):
        '''
        Test searching of players by team name

        We need to make sure that searching works AND that it still works with sorting
        '''
        # TODO: Make sure that it works with filtering as well

        # Searching for a part of a player team name with forward sort
        query = 'Bayern'
        players = get_players(offset=0, per_page=1000,
                              sort_by='goals', search_query=query)[0]

        goals = -1
        for player in players:
            self.assertTrue(player.goals >= goals)
            self.assertTrue(query in player.name
                            or query in player.position
                            or query in player.team_name)
            goals = player.goals

        # Searching for a part of a player team name with backward sort
        players = get_players(offset=0, per_page=1000,
                              sort_by='-goals', search_query=query)[0]

        goals = 10000
        for player in players:
            self.assertTrue(player.goals <= goals)
            self.assertTrue(query in player.name
                            or query in player.position
                            or query in player.team_name)
            goals = player.goals

    def test_search_teams(self):
        '''
        Test searching of teams

        We need to make sure that searching works AND that it still works with sorting
        '''
        # TODO: Make sure that it works with filtering as well
        # Forward sort
        teams = get_teams(offset=0, per_page=1000,
                          sort_by='name', search_query=None)[0]
        name = "A"
        for team in teams:
            self.assertTrue(team.name >= name)
            name = team.name

        # Backward sort
        teams = get_teams(offset=0, per_page=1000,
                          sort_by='-name', search_query=None)[0]
        name = "z"
        for team in teams:
            self.assertTrue(team.name <= name)
            name = team.name

    def test_search_matches(self):
        '''
        Test searching of matches

        We need to make sure that searching works AND that it still works with sorting
        '''
        # TODO: Make sure that it works with filtering as well
        # Forward sort
        matches = get_matches(offset=0, per_page=1000,
                              sort_by='date', search_query=None)[0]
        date = matches[0].date
        for match in matches:
            self.assertTrue(match.date >= date)
            date = match.date

        # Backward sort
        matches = get_matches(offset=0, per_page=1000,
                              sort_by='-date', search_query=None)[0]
        date = matches[0].date
        for match in matches:
            self.assertTrue(match.date <= date)
            date = match.date
