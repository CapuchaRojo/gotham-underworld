"""M013 bounded competition, compatibility, and campaign regressions."""
from copy import deepcopy
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from career_state import validate
from city_economy import advance as economy, on_job, summary as districts
from city_intelligence import dashboard, territory_history
from city_strategy import advance as strategy, assess, summary as strategy_summary
from district_missions import available, mission
from faction_campaigns import run_campaign
from faction_competition import active
from faction_profiles import PROFILES, summary
from faction_warfare import advance as warfare
from game_service import create_career, execute_command, advance_day, load_career, save_career
from gameplay import next_day, prepare
from simulation import new_world
from territory import capture


class FactionCompetitionTests(unittest.TestCase):
    def world(self, seed=42):
        world = create_career(seed)
        world['day'] = 2
        return world

    def plan_and_act(self, world):
        strategy(world, competition=True)
        return warfare(world, competition=True)

    def test_profiles_are_distinct_detached_and_persisted(self):
        world = self.world()
        self.assertEqual(len({tuple(sorted(p.items())) for p in PROFILES.values()}), 3)
        world['competition']['profiles']['trade_network']['recovery_income'] = 7
        self.assertEqual(PROFILES['trade_network']['recovery_income'], 6)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            save_career(world, path)
            self.assertEqual(load_career(path), world)

    def test_profile_identity_changes_income_and_operational_costs(self):
        a, b = self.world(), self.world()
        b['competition']['factions']['Harbor Syndicate'] = 'street_network'
        ea = economy(a, competition=True)
        eb = economy(b, competition=True)
        income_a = next(e['income'] for e in ea if e['kind'] == 'economy' and e['faction'] == 'Harbor Syndicate')
        income_b = next(e['income'] for e in eb if e['kind'] == 'economy' and e['faction'] == 'Harbor Syndicate')
        self.assertEqual((income_a, income_b), (5, 4))
        upkeep_a = next(e['upkeep'] for e in ea if e['kind'] == 'faction_economy' and e['faction'] == 'Harbor Syndicate')
        upkeep_b = next(e['upkeep'] for e in eb if e['kind'] == 'faction_economy' and e['faction'] == 'Harbor Syndicate')
        self.assertEqual((upkeep_a, upkeep_b), (4, 3))

    def test_displaced_zero_resource_faction_rebuilds_and_funds_an_offensive(self):
        world = create_career(42)
        faction = 'Carnival Crew'
        for district in world['districts'].values():
            district['owner'] = 'Harbor Syndicate'
        world['factions'][faction].update(cash=0, power=0)
        for _ in range(90):
            next_day(world, legal_rules=True)
        actions = [e for e in world['events'] if e['kind'] == 'faction_warfare' and e['faction'] == faction]
        self.assertTrue(any(e['action'] == 'recover' and e['cash_after'] > e['cash_before'] for e in actions))
        self.assertTrue(any(e['action'] == 'regroup' and e['power_after'] > e['power_before'] for e in actions))
        self.assertTrue(any(e['action'] == 'attack' and e['cost'] > 0 for e in actions))
        self.assertGreater(world['factions'][faction]['power'], 0)
        validate(world)

    def test_recovery_is_bounded_and_consumes_the_faction_turn(self):
        world = self.world()
        world['factions']['Harbor Syndicate'].update(cash=1, power=30)
        actions = self.plan_and_act(world)
        harbor = [e for e in actions if e['faction'] == 'Harbor Syndicate']
        self.assertEqual(len(harbor), 1)
        self.assertEqual(harbor[0]['action'], 'recover')
        self.assertEqual(harbor[0]['cash_after'] - harbor[0]['cash_before'], 6)
        self.assertEqual(harbor[0]['power_after'] - harbor[0]['power_before'], 2)
        before = deepcopy(world)
        self.assertEqual(warfare(world, competition=True), [])
        self.assertEqual(world, before)

    def test_recruitment_spends_money_and_restores_organizational_power(self):
        world = self.world()
        world['factions']['Iron Mask Outfit'].update(power=5, cash=20)
        action = next(e for e in self.plan_and_act(world) if e['faction'] == 'Iron Mask Outfit')
        self.assertEqual(action['action'], 'regroup')
        self.assertEqual(action['cash_before'] - action['cash_after'], 5)
        self.assertEqual(action['power_after'] - action['power_before'], 9)

    def test_no_negative_treasury_when_upkeep_is_unfunded(self):
        world = self.world()
        for data in world['factions'].values():
            data['cash'] = 0
        for d in world['districts'].values():
            d['owner'] = 'Civic Police'
        records = economy(world, competition=True)
        self.assertTrue(all(d['cash'] >= 0 for d in world['factions'].values()))
        self.assertTrue(all(e['paid'] == 0 for e in records if e['kind'] == 'faction_economy'))
        self.plan_and_act(world)
        validate(world)

    def test_income_caps_new_money_without_destroying_legacy_reserves(self):
        world = self.world()
        world['factions']['Harbor Syndicate']['cash'] = 1000
        records = economy(world, competition=True)
        income = next(e for e in records if e['kind'] == 'economy' and e['faction'] == 'Harbor Syndicate')
        self.assertEqual(income['income'], 0)
        self.assertGreater(world['factions']['Harbor Syndicate']['cash'], 900)
        self.assertLessEqual(world['factions']['Harbor Syndicate']['cash'], 1000)

    def test_power_stays_bounded_at_both_extremes(self):
        world = self.world()
        world['factions']['Harbor Syndicate'].update(power=100, cash=0)
        world['factions']['Iron Mask Outfit'].update(power=0, cash=0)
        for _ in range(40):
            next_day(world, legal_rules=True)
            self.assertTrue(all(0 <= d['power'] <= 100 and d['cash'] >= 0 for d in world['factions'].values()))
        validate(world)

    def test_modern_pressure_never_gives_away_territory(self):
        world = self.world()
        world['districts']['Harbor Docks']['control'] = 1
        economy(world, competition=True)
        self.assertEqual(world['districts']['Harbor Docks']['owner'], 'Harbor Syndicate')
        self.assertEqual(world['districts']['Harbor Docks']['control'], 1)
        self.assertEqual(territory_history(world), [])

    def test_legacy_pressure_claim_requires_resources(self):
        world = create_career()
        world['day'] = 1
        world['districts']['Harbor Docks']['control'] = 1
        for faction in ('Carnival Crew', 'Iron Mask Outfit'):
            world['factions'][faction].update(cash=0, power=0)
        economy(world)
        self.assertEqual(world['districts']['Harbor Docks']['owner'], 'Harbor Syndicate')
        self.assertFalse(territory_history(world))

    def test_paid_capture_has_complete_transfer_and_resource_metadata(self):
        world = self.world()
        world['districts']['Carnival Row']['control'] = 1
        action = next(e for e in self.plan_and_act(world) if e.get('captured'))
        self.assertEqual(action['strategy_objective'], 'expand')
        self.assertEqual(action['owner_after'], action['faction'])
        self.assertNotEqual(action['previous_owner'], action['owner_after'])
        self.assertEqual(action['control_after'], 35)
        self.assertEqual(action['control_at_capture'], 0)
        self.assertGreater(action['cost'], 0)
        self.assertEqual(action['cash_before'] - action['cost'], action['cash_after'])

    def test_ownership_operation_rejects_nonexhausted_control(self):
        world = self.world()
        before = deepcopy(world)
        with self.assertRaisesRegex(ValueError, 'exhausted'):
            capture(world, 'Carnival Row', 'Harbor Syndicate')
        self.assertEqual(world, before)

    def test_player_capture_uses_the_same_ownership_operation(self):
        world = create_career()
        execute_command(world, 'join', faction='Harbor Syndicate')
        world['districts']['Carnival Row']['control'] = 1
        response = execute_command(world, 'mission', kind='expand', district='Carnival Row')
        result = response['result']
        self.assertEqual(result['control_before'], 1)
        self.assertEqual(result['control_after'], 35)
        self.assertEqual(result['owner_after'], 'Harbor Syndicate')
        self.assertEqual(len(territory_history(world)), 1)
        self.assertEqual(response['actions_remaining'], 2)

    def test_lost_target_fallback_is_explicit_and_does_not_spend(self):
        world = self.world()
        strategy(world, competition=True)
        plan = world['faction_strategy']['Harbor Syndicate']
        world['districts'][plan['district']]['owner'] = 'Harbor Syndicate'
        before = world['factions']['Harbor Syndicate']['cash']
        action = next(e for e in warfare(world, competition=True) if e['faction'] == 'Harbor Syndicate')
        self.assertEqual(action['action'], 'hold')
        self.assertEqual(action['strategy_objective'], 'hold')
        self.assertEqual(action['planned_objective'], 'expand')
        self.assertTrue(action['fallback_reason'])
        self.assertEqual(action['strategy_reason'], action['fallback_reason'])
        self.assertEqual(world['factions']['Harbor Syndicate']['cash'], before)

    def test_unfunded_plan_and_changed_profile_hold(self):
        for change in ('funding', 'profile'):
            world = self.world()
            strategy(world, competition=True)
            if change == 'funding':
                world['factions']['Harbor Syndicate']['cash'] = 0
            else:
                world['competition']['factions']['Harbor Syndicate'] = 'street_network'
            action = next(e for e in warfare(world, competition=True) if e['faction'] == 'Harbor Syndicate')
            self.assertEqual(action['action'], 'hold')
            self.assertEqual(action['cost'], 0)
            self.assertTrue(action['fallback_reason'])

    def test_missing_plan_is_reassessed_and_explained(self):
        world = self.world()
        actions = warfare(world, competition=True)
        self.assertTrue(actions)
        self.assertTrue(all('reassessed' in e['fallback_reason'] for e in actions))
        self.assertTrue(all(e['strategy_objective'] == 'expand' for e in actions))

    def test_defense_priority_uses_economic_identity(self):
        world = self.world()
        world['districts']['Harbor Docks']['control'] = 50
        self.assertEqual(assess(world, 'Harbor Syndicate', competition=True)['objective'], 'expand')
        world['competition']['factions']['Harbor Syndicate'] = 'industrial_network'
        self.assertEqual(assess(world, 'Harbor Syndicate', competition=True)['objective'], 'defend')

    def test_custom_faction_binding_uses_the_same_engine(self):
        world = self.world()
        world['factions']['Example Organization'] = {'cash': 0, 'power': 0}
        world['competition']['factions']['Example Organization'] = 'street_network'
        self.assertEqual(assess(world, 'Example Organization', competition=True)['objective'], 'recover')
        economy(world, competition=True)
        actions = self.plan_and_act(world)
        self.assertTrue(any(e['faction'] == 'Example Organization' and e['action'] == 'recover' for e in actions))
        self.assertIn('Example Organization', {name for name, _ in strategy_summary(world)})
        self.assertIn('Example Organization', {row['faction'] for row in dashboard(world)['rankings']})
        validate(world)

    def test_dict_insertion_order_cannot_change_simulation_or_targeting(self):
        a, b = create_career(17), create_career(17)
        for key in ('factions', 'people', 'districts'):
            b[key] = dict(reversed(list(b[key].items())))
        for key in ('profiles', 'factions'):
            b['competition'][key] = dict(reversed(list(b['competition'][key].items())))
        for world in (a, b):
            execute_command(world, 'join', faction='Harbor Syndicate')
            world['districts']['Carnival Row']['owner'] = 'Harbor Syndicate'
            on_job(world, {'success': True, 'attempt': 0})
        self.assertEqual(available(a), available(b))
        for _ in range(30):
            advance_day(a); advance_day(b)
        self.assertEqual(a, b)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_each_daily_phase_is_idempotent(self):
        world = self.world()
        economy(world, competition=True)
        strategy(world, competition=True)
        warfare(world, competition=True)
        before = deepcopy(world)
        self.assertEqual(economy(world, competition=True), [])
        self.assertEqual(strategy(world, competition=True), [])
        self.assertEqual(warfare(world, competition=True), [])
        self.assertEqual(world, before)

    def test_old_save_initializes_without_mutating_historical_values(self):
        path = Path(__file__).parent / 'fixtures' / 'career_m012.json'
        old = json.loads(path.read_text(encoding='utf-8'))
        world = load_career(path)
        for key, value in old.items():
            self.assertEqual(world[key], value)
        self.assertEqual(world['competition']['activation_day'], world['day'] + 1)
        before = deepcopy(world)
        prepare(world)
        self.assertEqual(world, before)
        self.assertFalse(active(world))
        self.assertEqual(economy(world, competition=True), [])
        self.assertEqual(warfare(world, competition=True), [])
        advance_day(world)
        self.assertTrue(active(world))
        validate(world)

    def test_mid_campaign_disk_resume_is_equivalent(self):
        a, b = create_career(99), create_career(99)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'career.json'
            for day in range(60):
                advance_day(a); advance_day(b)
                if day % 11 == 0:
                    save_career(b, path)
                    b = load_career(path)
                    self.assertEqual(a, b)
            validate(a)
            self.assertEqual(a, b)

    def test_profile_schema_and_economic_events_reject_invalid_state(self):
        mutations = [lambda w: w.update(competition_version=999), lambda w: w.update(competition_version=True),
                     lambda w: w.pop('competition'), lambda w: w.pop('competition_version'),
                     lambda w: w['competition']['factions'].update({'unknown': 'street_network'}),
                     lambda w: w['competition']['factions'].update({'Harbor Syndicate': 'unknown'}),
                     lambda w: w['competition']['profiles']['trade_network'].update(recovery_income=0),
                     lambda w: w['competition']['profiles']['trade_network'].update(recovery_cap=1),
                     lambda w: w['competition']['profiles']['trade_network'].update(treasury_cap=True),
                     lambda w: w['competition'].update(activation_day=999)]
        for change in mutations:
            world = self.world(); change(world)
            with self.assertRaisesRegex(ValueError, 'competition'):
                validate(world)
        world = self.world()
        economy(world, competition=True)
        world['events'][-1]['cash_after'] = -1
        with self.assertRaisesRegex(ValueError, 'competition.events'):
            validate(world)

    def test_profiles_and_intelligence_are_detached_read_models(self):
        world = self.world()
        before = deepcopy(world)
        report = dashboard(world)
        report['competition'][0]['rules']['attack_cost'] = 999
        summary(world)[0]['rules']['recovery_income'] = 0
        districts(world)[0][1]['control'] = -1
        self.assertEqual(world, before)

    def test_saturated_recovery_holds_without_fabricating_activity(self):
        world = self.world()
        for district in world['districts'].values():
            district.update(owner='Harbor Syndicate', control=100)
        world['factions']['Harbor Syndicate'].update(cash=240, power=100)
        for name in ('Carnival Crew', 'Iron Mask Outfit'):
            world['factions'][name].update(cash=0, power=0)
        action = next(e for e in self.plan_and_act(world) if e['faction'] == 'Harbor Syndicate')
        self.assertEqual(action['action'], 'hold')
        self.assertIn('capacity', action['fallback_reason'])
        self.assertEqual(action['cash_after'], action['cash_before'])

    def test_initiative_rotates_without_extra_random_draws(self):
        first = []
        for day in (2, 3, 4):
            world = self.world(); world['day'] = day
            first.append(self.plan_and_act(world)[0]['faction'])
        self.assertEqual(len(set(first)), 3)

    def test_recovery_income_stops_at_its_capacity(self):
        world = self.world()
        world['factions']['Harbor Syndicate'].update(cash=59, power=30)
        strategy(world, competition=True)
        world['faction_strategy']['Harbor Syndicate'].update(objective='recover', district=None)
        action = next(e for e in warfare(world, competition=True) if e['faction'] == 'Harbor Syndicate')
        self.assertEqual(action['income'], 1)
        self.assertEqual(action['cash_after'], 60)

    def test_unprepared_profile_query_does_not_initialize_state(self):
        world = new_world()
        before = deepcopy(world)
        self.assertEqual(summary(world), [])
        with self.assertRaises(ValueError):
            assess(world, 'Harbor Syndicate', competition=True)
        self.assertEqual(world, before)

    def test_canonical_wait_and_daily_reducer_have_identical_faction_effects(self):
        a, b = create_career(17), create_career(17)
        for _ in range(12):
            advance_day(a)
            next_day(b, legal_rules=True)
        self.assertEqual(a['factions'], b['factions'])
        self.assertEqual(a['districts'], b['districts'])
        self.assertEqual([e for e in a['events'] if e['kind'] != 'player_command'], b['events'])

    def test_transfer_history_reconstructs_ownership(self):
        world = create_career(42)
        owners = {name: d['owner'] for name, d in world['districts'].items()}
        for _ in range(365):
            next_day(world, legal_rules=True)
        history = territory_history(world, len(world['events']))
        self.assertTrue(history)
        for transfer in history:
            district = transfer['district']
            self.assertEqual(owners[district], transfer['previous_owner'])
            self.assertEqual(transfer['owner_after'], transfer['faction'])
            owners[district] = transfer['owner_after']
        self.assertEqual(owners, {name: d['owner'] for name, d in world['districts'].items()})

    def test_four_year_campaigns_and_a_thousand_days_enforce_bounds_not_winners(self):
        for seed, days in ((1, 365), (17, 365), (42, 365), (99, 365), (42, 1000)):
            with self.subTest(seed=seed, days=days):
                result = run_campaign(seed, days)
                self.assertEqual(result['bound_violations'], 0)
                self.assertEqual(sum(row['districts'] for row in result['factions'].values()), 3)
                # Winning/remaining active is measured by the report, not forced.
                self.assertEqual(result['days'], days)

    def test_fresh_process_determinism_and_global_rng_isolation(self):
        state = random.getstate()
        world = self.world()
        economy(world, competition=True); self.plan_and_act(world)
        self.assertEqual(state, random.getstate())
        code = 'import json;from faction_campaigns import run_campaign;print(json.dumps(run_campaign(17,40),sort_keys=True))'
        output = [subprocess.check_output([sys.executable, '-B', '-c', code],
                  cwd=Path(__file__).resolve().parents[1], env=dict(os.environ, PYTHONHASHSEED=seed), text=True)
                  for seed in ('0', '42')]
        self.assertEqual(output[0], output[1])


if __name__ == '__main__':
    unittest.main()
