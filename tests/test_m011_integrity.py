"""M011 integration corrections outside the career command boundary."""
from copy import deepcopy
import unittest

from city_intelligence import dashboard, territory_history
from city_strategy import advance as plan, assess, summary
from consequence_engine import investigate
from faction_warfare import advance as warfare
from gameplay import next_day, prepare
from npc_actions import act
from relationship_engine import change, decision
from simulation import event, new_world, resolve_case


class IntegrityTests(unittest.TestCase):
    def pending_world(self):
        world = prepare(new_world())
        world['cases'].append({'id': 1, 'crime': 'collection intimidation', 'suspect': 'Rookie',
                               'status': 'pending', 'evidence': 1, 'witnessed': True,
                               'source_attempt': 0, 'investigation_days': 0})
        return world

    def test_daily_investigation_is_idempotent_per_case(self):
        world = self.pending_world()
        investigate(world)
        before = deepcopy(world)
        investigate(world)
        self.assertEqual(world, before)
        self.assertEqual(world['cases'][0]['evidence'], 2)
        world['day'] += 1
        investigate(world)
        self.assertEqual(world['cases'][0]['evidence'], 3)
        self.assertTrue(world['player']['arrested'])
        resolve_case(world)
        self.assertEqual(world['player']['custody'], 'free')

    def test_npc_acceleration_survives_daily_guard(self):
        world = self.pending_world()
        change(world, 'Detective Vale', {'suspicion': 16}, 'test')
        investigate(world)
        act(world)
        self.assertEqual(world['cases'][0]['evidence'], 3)
        self.assertEqual(world['cases'][0]['investigation_days'], 1)
        self.assertEqual(world['cases'][0]['status'], 'charged')
        self.assertTrue(any(e.get('cause') == 'npc_evidence_review' for e in world['events']))

    def test_multiple_cases_resolve_with_consistent_custody(self):
        world = self.pending_world()
        second = deepcopy(world['cases'][0]); second['id'] = 2
        world['cases'].append(second)
        for _ in range(4):
            next_day(world)
        self.assertTrue(all(case['status'] == 'convicted' for case in world['cases']))
        self.assertFalse(world['player']['arrested'])
        self.assertEqual(world['player']['custody'], 'free')

    def test_lost_defense_target_holds_with_explicit_reason(self):
        world = prepare(new_world()); world['day'] = 2
        world['districts']['Carnival Row']['control'] = 1
        world['factions']['Carnival Crew']['cash'] = 100
        plan(world)
        before = world['factions']['Carnival Crew']['cash']
        actions = warfare(world)
        carnival = next(e for e in actions if e['faction'] == 'Carnival Crew')
        self.assertEqual(carnival['action'], 'hold')
        self.assertEqual(carnival['strategy_objective'], 'hold')
        self.assertEqual(carnival['planned_objective'], 'defend')
        self.assertIn('no longer owned', carnival['fallback_reason'])
        self.assertEqual(world['factions']['Carnival Crew']['cash'], before)
        snapshot = deepcopy(world)
        self.assertEqual(warfare(world), [])
        self.assertEqual(world, snapshot)

    def test_expansion_target_now_owned_holds(self):
        world = prepare(new_world()); world['day'] = 2
        plan(world)
        target = world['faction_strategy']['Harbor Syndicate']['district']
        world['districts'][target]['owner'] = 'Harbor Syndicate'
        action = next(e for e in warfare(world) if e['faction'] == 'Harbor Syndicate')
        self.assertEqual(action['action'], 'hold')
        self.assertEqual(action['planned_objective'], 'expand')
        self.assertIn('no longer available', action['fallback_reason'])

    def test_unfunded_defense_cannot_fall_through_to_attack(self):
        world = prepare(new_world()); world['day'] = 2
        world['districts']['Harbor Docks']['control'] = 20
        plan(world)
        world['factions']['Harbor Syndicate']['cash'] = 0
        action = next(e for e in warfare(world) if e['faction'] == 'Harbor Syndicate')
        self.assertEqual(action['action'], 'hold')
        self.assertIn('funding', action['fallback_reason'])

    def test_expired_plan_uses_explained_legacy_policy(self):
        world = prepare(new_world()); world['day'] = 2
        plan(world)
        world['faction_strategy']['Harbor Syndicate']['day'] = 1
        action = next(e for e in warfare(world) if e['faction'] == 'Harbor Syndicate')
        self.assertEqual(action['action'], 'attack')
        self.assertEqual(action['strategy_objective'], 'expand')
        self.assertIn('legacy warfare policy', action['fallback_reason'])

    def test_assessment_and_summary_do_not_prepare_legacy_world(self):
        world = new_world()
        before = deepcopy(world)
        self.assertEqual(assess(world, 'Harbor Syndicate')['owned_count'], 0)
        self.assertEqual(decision(world, 'Mara Voss')['action'], 'neutral')
        self.assertEqual(summary(world), [(name, None) for name in ('Harbor Syndicate', 'Carnival Crew', 'Iron Mask Outfit')])
        self.assertEqual(world, before)

    def test_reports_cannot_mutate_nested_events_or_plans(self):
        world = prepare(new_world()); world['day'] = 2
        plan(world)
        event(world, 'district_mission', 'Capture', captured=True, metadata={'nested': [1]})
        before = deepcopy(world)
        report = dashboard(world)
        report['territory_history'][0]['metadata']['nested'].append(2)
        territory_history(world)[0]['message'] = 'edited'
        summary(world)[0][1]['reason'] = 'edited'
        self.assertEqual(world, before)


if __name__ == '__main__':
    unittest.main()
