"""M010 regression tests for read-only city intelligence."""
import copy
import json
import unittest
from simulation import new_world, event
from gameplay import prepare, next_day, join
from district_missions import mission
from city_intelligence import rankings, territory_history, player_influence, briefing, dashboard


class CityIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.world = prepare(new_world(42))

    def test_initial_rankings(self):
        self.assertEqual(len(rankings(self.world)), 3)
        self.assertEqual({r['districts'] for r in rankings(self.world)}, {1})

    def test_rankings_reflect_ownership(self):
        self.world['districts']['Carnival Row']['owner'] = 'Harbor Syndicate'
        self.assertEqual(rankings(self.world)[0]['faction'], 'Harbor Syndicate')
        self.assertEqual(rankings(self.world)[0]['districts'], 2)

    def test_rankings_deterministic_ties(self):
        self.assertEqual(rankings(self.world), rankings(copy.deepcopy(self.world)))

    def test_history_excludes_attacks(self):
        event(self.world, 'faction_warfare', 'Attack only', captured=False)
        self.assertEqual(territory_history(self.world), [])

    def test_history_includes_three_capture_types(self):
        event(self.world, 'territory', 'Economic capture', cause='control_exhausted')
        event(self.world, 'faction_warfare', 'Warfare capture', captured=True)
        event(self.world, 'district_mission', 'Player capture', captured=True)
        self.assertEqual(len(territory_history(self.world)), 3)
        self.assertEqual(len(territory_history(self.world, 2)), 2)

    def test_history_zero_and_negative_limit(self):
        self.assertEqual(territory_history(self.world, 0), [])
        with self.assertRaises(ValueError): territory_history(self.world, -1)

    def test_player_influence_is_attributed(self):
        join(self.world, 'Harbor Syndicate')
        mission(self.world, 'expand', 'Carnival Row')
        event(self.world, 'faction_warfare', 'NPC attack', captured=True)
        influence = player_influence(self.world)
        self.assertEqual(influence['expansions'], 1)
        self.assertEqual(influence['captures'], 0)

    def test_briefing_daily_income(self):
        next_day(self.world)
        self.assertEqual(briefing(self.world)['income'], 10)
        self.assertEqual(briefing(self.world)['day'], 1)

    def test_briefing_rejects_future(self):
        with self.assertRaises(ValueError): briefing(self.world, 2)

    def test_dashboard_read_only(self):
        before = json.dumps(self.world, sort_keys=True)
        dashboard(self.world)
        self.assertEqual(json.dumps(self.world, sort_keys=True), before)

    def test_save_round_trip_report(self):
        next_day(self.world)
        restored = json.loads(json.dumps(self.world))
        self.assertEqual(dashboard(self.world), dashboard(restored))

    def test_full_day_determinism(self):
        a = prepare(new_world(99)); b = prepare(new_world(99))
        for _ in range(3): next_day(a); next_day(b)
        self.assertEqual(dashboard(a), dashboard(b))


if __name__ == '__main__': unittest.main()
