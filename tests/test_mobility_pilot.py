"""Station service behavior through the authoritative player boundary."""
from copy import deepcopy
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest
from unittest.mock import patch

from career_state import validate
from game_service import actions_remaining, advance_day, create_career, execute_command
import mobility
import mobility_content
import navigation


def adopted(seed=42, cash=40, life=False):
    world = create_career(seed)
    world['player']['cash'] = cash
    if life:
        execute_command(world, 'settle_in')
    execute_command(world, 'travel', destination='p039', mode='auto')
    execute_command(world, 'enable_mobility', overlay_id=mobility_content.OVERLAY_ID, request_id='adopt.first')
    advance_day(world)
    return world


def move(world, destination, profile='fastest', **limits):
    quote = mobility.plan_route(world, destination, profile, **limits)
    return execute_command(world, 'journey', **quote['arguments'])


class MobilityPilotTests(unittest.TestCase):
    def rejected(self, world, command, **args):
        before, rng = deepcopy(world), random.getstate()
        with self.assertRaises(ValueError):
            execute_command(world, command, **args)
        self.assertEqual(before, world)
        self.assertEqual(rng, random.getstate())

    def closure(self, world, *, mode='rail', known=False, origin='n18', edge='e06'):
        world['navigation']['closures'].append(dict(id='fixture.closure', edge_id='goon.edge.' + edge,
            from_id='goon.neighborhood.' + origin, mode=mode, start_day=world['day'],
            end_day=world['day'] + 2, known=known, cause='authored_test'))
        validate(world)

    def test_overlay_is_detached_pinned_and_geographically_contiguous(self):
        data = mobility_content.load()
        self.assertEqual(data['base_atlas_fingerprint'], navigation.fingerprint())
        self.assertEqual([s['place_id'] for s in data['stations']], ['goon.poi.p039', 'goon.poi.p071'])
        data['line']['fare'] = 0
        self.assertEqual(mobility_content.load()['line']['fare'], 2)
        for mutate in (lambda d: d['line'].update(ride_tu=5),
                       lambda d: d['line']['segments'][2].update(from_id='goon.neighborhood.n22'),
                       lambda d: d['stations'][0].update(place_id='goon.poi.p031'),
                       lambda d: d.update(overlay_version=True)):
            invalid = mobility_content.load()
            mutate(invalid)
            with self.assertRaises(ValueError):
                mobility_content.validate(invalid)

    def test_station_roundtrip_exact_7tu_2dollar_no_action_or_day_cost(self):
        world = adopted()
        initial_day = world['day']
        for end in ('p071', 'p039'):
            quote = mobility.plan_route(world, end, 'monorail')
            self.assertEqual((quote['cost'], quote['fare']), (7, 2))
            self.assertEqual([l['kind'] for l in quote['legs']], ['walk_gate', 'board', 'ride', 'alight', 'walk_gate'])
            result = execute_command(world, 'journey', **quote['arguments'])['result']
            self.assertEqual(result['resources']['cash']['cost'], 2)
        self.assertEqual((world['navigation']['tu_used'], world['player']['cash']), (14, 36))
        self.assertEqual((world['day'], actions_remaining(world)), (initial_day, 3))

    def test_remote_origin_requires_actual_approach_not_remote_boarding(self):
        world = adopted()
        move(world, 'home', 'free')
        quote = mobility.plan_route(world, 'p071', 'monorail')
        self.assertEqual(quote['cost'], 11)  # four walking approach TU plus 7 station TU
        self.assertEqual(quote['legs'][0]['from_id'], 'goon.poi.p031')
        board = next(l for l in quote['legs'] if l['kind'] == 'board')
        self.assertEqual(board['from_id'], 'goon.mobility.node.p039.platform')
        self.rejected(world, 'board', station='p039')
        self.rejected(world, 'journey', **dict(quote['arguments'], max_tu='7'))

    def test_monorail_request_cannot_board_at_a_neighborhood(self):
        world = adopted()
        move(world, 'n17', 'walk')
        result = move(world, 'p071', 'monorail')['result']
        self.assertEqual(result['legs'][0]['kind'], 'move')
        self.assertEqual(result['legs'][0]['to_id'], 'goon.poi.p039')
        self.assertEqual(result['resources']['tu']['cost'], 7)

    def test_same_place_cannot_farm_resources(self):
        world = adopted()
        quote = mobility.plan_route(world, 'p039', 'monorail')
        self.rejected(world, 'journey', **quote['arguments'])

    def test_return_projection_consumes_outbound_cash_and_offers_free_return(self):
        world = adopted(cash=2)
        before = deepcopy(world)
        quote = mobility.plan_route(world, 'p071', 'monorail')
        self.assertTrue(quote['affordable'])
        self.assertFalse(quote['return_fits_today'])
        self.assertEqual((quote['return_cost'], quote['return_fare'], quote['free_return_cost']), (7, 2, 8))
        self.assertTrue(quote['can_return_today'])
        self.assertTrue(quote['return_uncertain'])
        self.assertEqual(world, before)  # declining the quote has no effect

    def test_outbound_caps_do_not_erase_real_return_resources(self):
        world = adopted()
        quote = mobility.plan_route(world, 'p071', 'monorail', max_tu='7', max_cash='2')
        self.assertTrue(quote['affordable'])
        self.assertTrue(quote['return_fits_today'])
        execute_command(world, 'journey', **quote['arguments'])
        self.assertEqual((18-world['navigation']['tu_used'], world['player']['cash']), (11, 38))

    def test_remote_zero_cash_tu_shortfall_has_explicit_next_day_recovery(self):
        world = adopted(cash=2)
        for end in ('n17', 'p039', 'n17', 'p039'):
            move(world, end, 'walk')
        quote = mobility.plan_route(world, 'p071', 'monorail')
        self.assertTrue(quote['affordable'])
        self.assertFalse(quote['can_return_today'])
        execute_command(world, 'journey', **quote['arguments'])
        self.assertEqual((18-world['navigation']['tu_used'], world['player']['cash']), (7, 0))
        q = mobility.plan_route(world, 'p039', 'bus')
        self.assertFalse(q['affordable'])
        self.rejected(world, 'journey', **q['arguments'])
        advance_day(world)
        move(world, 'p039', 'bus')
        self.assertEqual(world['player']['cash'], 0)

    def test_insufficient_cash_is_atomic(self):
        world = adopted(cash=1)
        q = mobility.plan_route(world, 'p071', 'monorail')
        self.assertEqual(q['status'], 'unaffordable')
        self.rejected(world, 'journey', **q['arguments'])
        self.assertTrue(mobility.plan_route(world, 'p071', 'free')['affordable'])

    def test_insufficient_tu_and_exact_boundary(self):
        world = adopted()
        for _ in range(6):
            move(world, 'n17', 'walk')
            move(world, 'p039', 'walk')
        q = mobility.plan_route(world, 'p071', 'monorail')
        self.rejected(world, 'journey', **q['arguments'])
        for _ in range(3):
            move(world, 'n17', 'walk')
            move(world, 'p039', 'walk')
        self.assertEqual(world['navigation']['tu_used'], 18)
        q = mobility.plan_route(world, 'n17', 'walk')
        self.rejected(world, 'journey', **q['arguments'])
        before = deepcopy(world)
        mobility.mobility_report(world)
        navigation.begin_day(world)
        self.assertEqual(before, world)

    def test_stale_quote_cannot_commit_or_charge(self):
        world = adopted()
        quote = mobility.plan_route(world, 'p071', 'monorail')
        move(world, 'n17', 'walk')
        self.rejected(world, 'journey', **quote['arguments'])

    def test_duplicate_request_recovers_receipt_without_repeat_fare(self):
        world = adopted()
        quote = mobility.plan_route(world, 'p071', 'monorail')
        execute_command(world, 'journey', **quote['arguments'])
        self.rejected(world, 'journey', **quote['arguments'])
        receipt = mobility.mobility_receipt(world, quote['arguments']['request_id'])
        receipt['charge_ids'].clear()
        self.assertEqual(len(mobility.mobility_receipt(world, quote['arguments']['request_id'])['charge_ids']), 1)

    def test_legacy_rail_and_travel_command_cannot_bypass_active_policy(self):
        world = adopted()
        with self.assertRaises(ValueError):
            navigation.plan_route(world, 'p071', 'rail')
        self.rejected(world, 'travel', destination='p071', mode='rail')
        self.rejected(world, 'travel', destination='p071', mode='walk')

    def test_bus_and_ferry_retain_free_base_costs(self):
        world = adopted()
        self.assertEqual((mobility.plan_route(world, 'p071', 'bus')['cost'],
                          mobility.plan_route(world, 'p071', 'bus')['fare']), (8, 0))
        move(world, 'n18', 'bus')
        # Existing ferry e16 joins n18/n23; compare against the unmodified v1 search.
        places, edges = navigation._definitions()
        for edge in edges.values():
            if 'ferry' in edge['modes']:
                # A fresh valid location fixture avoids introducing fake journeys.
                legacy = create_career()
                legacy['navigation']['location_id'] = edge['from']
                legacy['navigation']['permissions'].append(edge['to'])
                expected = navigation.plan_route(legacy, edge['to'], 'ferry')['cost']
                quote_world = deepcopy(world)
                quote_world['navigation']['location_id'] = edge['from']
                quote_world['navigation']['permissions'].append(edge['to'])
                q = mobility.plan_route(quote_world, edge['to'], 'ferry')
                self.assertEqual((q['cost'], q['fare']), (expected, 0))

    def test_known_line_closure_hides_no_free_fallback(self):
        world = adopted()
        self.closure(world, known=True)
        q = mobility.plan_route(world, 'p071', 'monorail')
        self.assertEqual(q['status'], 'no_known_route')
        self.rejected(world, 'journey', **q['arguments'])
        move(world, 'p071', 'bus')
        self.assertEqual(world['player']['cash'], 40)

    def test_unknown_line_closure_discovery_costs_zero_before_boarding(self):
        world = adopted()
        before = mobility.plan_route(world, 'p071', 'monorail')
        self.closure(world)
        after = mobility.plan_route(world, 'p071', 'monorail')
        self.assertEqual(before, after)
        result = execute_command(world, 'journey', **after['arguments'])['result']
        self.assertTrue(result['interrupted'])
        self.assertEqual((result['arrived'], result['resources']['tu']['cost'], result['resources']['cash']['cost']), ('goon.poi.p039', 0, 0))
        self.assertEqual(result['legs'], [])
        self.assertFalse(world['navigation']['closures'][0]['known'])
        self.assertEqual(mobility.plan_route(world, 'p071', 'monorail')['status'], 'no_known_route')

    def test_unknown_line_closure_charges_actual_approach_floor_only(self):
        world = adopted()
        move(world, 'n17', 'walk')
        self.closure(world)
        result = move(world, 'p071', 'monorail')['result']
        self.assertEqual((result['resources']['tu']['cost'], result['resources']['cash']['cost']), (1, 0))
        self.assertEqual((result['arrived'], len(result['legs'])), ('goon.poi.p039', 1))

    def test_quote_tokens_do_not_reveal_private_disruption_provenance(self):
        world = adopted()
        self.closure(world)
        move(world, 'p071', 'monorail')  # observes only service-level unavailability
        other = deepcopy(world)
        other['navigation']['closures'][0].update(id='another.private.source', cause='hidden cause')
        for observation in other['mobility']['knowledge']['service_disruptions']:
            observation['source_ids'] = ['another.private.source']
        for e in other['events']:
            if e['kind'] == 'travel' and e.get('schema_version') == 2:
                for observation in e['discoveries']:
                    observation['source_ids'] = ['another.private.source']
        validate(other)
        self.assertEqual(mobility.mobility_report(world), mobility.mobility_report(other))
        self.assertEqual(mobility.plan_route(world, 'p071', 'monorail'),
                         mobility.plan_route(other, 'p071', 'monorail'))

    def test_ground_unknown_closure_keeps_safe_bus_prefix(self):
        world = adopted()
        self.closure(world, mode='bus')
        result = move(world, 'p071', 'bus')['result']
        self.assertEqual((result['arrived'], result['resources']['tu']['cost']), ('goon.neighborhood.n18', 2))
        self.assertEqual(result['resources']['cash']['cost'], 0)
        self.assertTrue(world['navigation']['closures'][0]['known'])

    def test_line_direction_and_finite_reopening(self):
        world = adopted()
        self.closure(world, known=True)
        move(world, 'p071', 'bus')
        self.assertTrue(mobility.plan_route(world, 'p039', 'monorail')['affordable'])
        move(world, 'p039', 'monorail')
        advance_day(world)
        self.assertEqual(mobility.plan_route(world, 'p071', 'monorail')['status'], 'no_known_route')
        advance_day(world)
        self.assertEqual(mobility.plan_route(world, 'p071', 'monorail')['cost'], 7)

    def test_reports_quotes_and_nested_references_are_pure(self):
        world = adopted()
        before, rng = deepcopy(world), random.getstate()
        for _ in range(3):
            q = mobility.plan_route(world, 'p071', 'monorail')
            q['legs'][0]['tu'] = 99
            q['arguments']['destination'] = 'bad'
            mobility.mobility_report(world)['stations'].clear()
        self.assertEqual(world, before)
        self.assertEqual(rng, random.getstate())
        empty = create_career()
        before = deepcopy(empty)
        self.assertEqual(mobility.mobility_report(empty)['status'], 'disabled')
        self.assertEqual(before, empty)

    def test_insertion_order_and_hash_seeds_do_not_change_plans_or_state(self):
        world = adopted()
        expected = mobility.plan_route(world, 'p071', 'monorail')
        places, edges = navigation._definitions()
        reversed_edges = dict(reversed(list(edges.items())))
        for e in reversed_edges.values():
            e['modes'] = dict(reversed(list(e['modes'].items())))
        with patch('navigation._definitions', return_value=(dict(reversed(list(places.items()))), reversed_edges)):
            self.assertEqual(expected, mobility.plan_route(world, 'p071', 'monorail'))
        code = ('import json,hashlib;from game_service import *;import mobility;from mobility_content import OVERLAY_ID;'
                'w=create_career(42);execute_command(w,"travel",destination="p039",mode="auto");'
                'execute_command(w,"enable_mobility",overlay_id=OVERLAY_ID,request_id="adopt");advance_day(w);'
                'q=mobility.plan_route(w,"p071","monorail");execute_command(w,"journey",**q["arguments"]);'
                'print(hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest())')
        out = [subprocess.check_output([sys.executable, '-B', '-c', code], cwd=Path(__file__).resolve().parents[1],
               env=dict(os.environ, PYTHONHASHSEED=s), text=True) for s in ('0', '42')]
        self.assertEqual(out[0], out[1])

    def test_search_limit_is_explicit_and_atomic(self):
        world = adopted()
        before = deepcopy(world)
        with patch('mobility.MAX_LABELS', 0), self.assertRaises(mobility.PlanningLimit):
            mobility.plan_route(world, 'p071', 'monorail')
        self.assertEqual(before, world)

    def test_fare_uses_one_existing_daily_life_balance_projection(self):
        world = adopted(life=True)
        before = len(world['daily_life']['transactions'])
        move(world, 'p071', 'monorail')
        self.assertEqual(world['player']['cash'], 38)
        self.assertEqual(len(world['daily_life']['transactions']), before + 1)
        self.assertEqual(world['daily_life']['transactions'][-1]['amount'], -2)
        validate(world)

    def test_custody_does_not_allow_travel_or_adoption(self):
        world = adopted()
        world['cases'].append(dict(id=1, crime='fixture', suspect='Rookie', status='charged', evidence=3))
        world['player'].update(arrested=True, custody='pretrial')
        validate(world)
        before = deepcopy(world)
        with self.assertRaises(ValueError):
            mobility.plan_route(world, 'p071')
        self.assertEqual(before, world)
        self.assertEqual(mobility.mobility_report(world)['status'], 'active')

    def test_malformed_arguments_and_vehicle_scope_reject_atomically(self):
        world = adopted()
        q = mobility.plan_route(world, 'p071', 'monorail')
        for key, value in (('max_tu', '-1'), ('max_tu', '19'), ('max_cash', '02'),
                           ('vehicle_id', 'car.1'), ('quote_token', 'bad'), ('request_id', '../file')):
            self.rejected(world, 'journey', **dict(q['arguments'], **{key: value}))

    def test_three_spent_gameplay_actions_do_not_disable_remaining_travel(self):
        world = adopted()
        execute_command(world, 'join', faction='Harbor Syndicate')
        for _ in range(3):
            execute_command(world, 'job', kind='courier')
        self.assertEqual(actions_remaining(world), 0)
        move(world, 'n17', 'walk')
        self.assertEqual((actions_remaining(world), world['navigation']['tu_used']), (0, 1))
        self.rejected(world, 'job', kind='courier')

    def test_restricted_institution_and_unknown_place_reject_without_mutation(self):
        world = adopted()
        for target in ('p112', 'p031.private', 'goon.mobility.node.p071.platform'):
            before = deepcopy(world)
            try:
                quote = mobility.plan_route(world, target, 'free')
            except ValueError:
                self.assertEqual(world, before)
            else:
                self.rejected(world, 'journey', **quote['arguments'])
