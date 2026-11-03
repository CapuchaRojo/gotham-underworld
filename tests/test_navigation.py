import contextlib
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from career_state import validate
import gameplay
from game_service import (create_career, execute_command, advance_day, save_career,
                          load_career, location_report, nearby_destinations, known_places, plan_route, snapshot)
import location_registry
import navigation


class RegistryTests(unittest.TestCase):
    def test_complete_atlas_matches_documented_places(self):
        data = location_registry.load()
        counts = {kind: sum(p['kind'] == kind for p in data['places']) for kind in ('region','neighborhood','poi')}
        self.assertEqual(counts, dict(region=8, neighborhood=48, poi=120))
        self.assertEqual(sum(e['kind'] == 'corridor' for e in data['edges']), 63)
        self.assertEqual(sum(e['kind'] == 'access' for e in data['edges']), 120)
        # Compare every source row's identity, spelling, parent and profile, not only counts.
        import re
        source = Path(__file__).resolve().parents[1] / 'docs/GOON_LOCATION_REGISTRY.md'
        rows = [line for line in source.read_text(encoding='utf-8').splitlines() if re.match(r'\| `goon\.(region|neighborhood|poi)\.',line)]
        places = {p['id']:p for p in data['places']}
        for line in rows:
            c = [v.strip() for v in line.strip('|').split('|')]
            p = places[c[0].strip('`')]
            self.assertEqual(p['label'], c[1])
            self.assertEqual(p['parent_id'], re.findall(r'`([^`]+)`',c[2])[0])
            for key, value in zip(('access','economy','security','criminal','civilian','npc_pool'), c[4:10]):
                self.assertEqual(p[key], value.split('+'))
        self.assertEqual(len(rows),176)

    def test_invalid_registry_references_versions_costs_and_spurs(self):
        mutations = [lambda d: d.update(atlas_version=True), lambda d:d.update(atlas_version=2),
            lambda d:d['places'].append(deepcopy(d['places'][0])),
            lambda d:d['places'][0].update(parent_id='bad'),
            lambda d:d['places'][-1].update(region_id='bad'),
            lambda d:d['places'][9].update(access=['MAGIC']),
            lambda d:d['edges'][0].update(to=[]),
            lambda d:d['edges'][0].update(modes={'walk':-1}),
            lambda d:d['edges'][0].update(modes={'walk':True}),
            lambda d:d['edges'][0].update(modes={'teleport':1}),
            lambda d:d['edges'][0].update(bidirectional=1),
            lambda d:d['edges'].pop(),
            lambda d:d['edges'][-1].update(modes={'walk':-1})]
        for mutate in mutations:
            d = location_registry.load(); mutate(d)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError): location_registry.validate(d)

    def test_detached_catalog_and_duplicate_json(self):
        data = location_registry.load();data['places'].clear()
        self.assertEqual(len(location_registry.load()['places']),176)
        with self.assertRaises(ValueError): location_registry._unique([('id',1),('id',2)])


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.world = create_career(42)

    def move(self, destination, mode='auto', world=None):
        return execute_command(world if world is not None else self.world, 'travel', destination=destination, mode=mode)

    def closure(self, edge='e06', origin='n18', mode='bus', known=True, ident='closure.1', world=None):
        w = world if world is not None else self.world
        c = dict(id=ident,edge_id='goon.edge.'+edge,from_id='goon.neighborhood.'+origin,
                 mode=mode,start_day=w['day'],end_day=w['day']+2,known=known,cause='maintenance.fixture')
        w['navigation']['closures'].append(c)
        return c

    def rejected(self, callback):
        before = deepcopy(self.world)
        with self.assertRaises(ValueError): callback()
        self.assertEqual(self.world,before)

    def test_home_store_return_day_and_disk_resume(self):
        self.assertEqual(location_report(self.world)['place']['label'],'East Side Housing Cooperative')
        self.assertIn('goon.poi.p032',[p['id'] for p in nearby_destinations(self.world)])
        self.move('p032');self.assertEqual(location_report(self.world)['place']['type'],'shop')
        self.move('home');self.assertEqual(self.world['navigation']['tu_used'],2)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'career.json';save_career(self.world,path)
            resumed=load_career(path);self.assertEqual(resumed,self.world)
            advance_day(resumed);self.assertEqual(resumed['navigation']['tu_used'],0)
            self.assertEqual(resumed['navigation']['location_id'],'goon.poi.p031')
            validate(resumed)

    def test_shared_actions_and_existing_jobs_remain_independent(self):
        execute_command(self.world,'join',faction='Harbor Syndicate')
        for _ in range(3):execute_command(self.world,'job',kind='courier')
        self.move('p032');self.move('home')
        self.assertEqual(self.world['actions_used'],3)
        self.rejected(lambda:execute_command(self.world,'job',kind='courier'))
        self.assertEqual(self.world['job_attempts'],3)

    def test_eighteen_local_moves_exhaust_tu_without_free_movement(self):
        for i in range(18):self.move('p032' if i%2==0 else 'home')
        self.assertEqual(self.world['navigation']['tu_used'],18)
        self.rejected(lambda:self.move('p032'))
        self.assertEqual(self.world['actions_used'],0)
        advance_day(self.world);self.move('p032')

    def test_queries_never_initialize_refresh_or_leak_references(self):
        before=deepcopy(self.world)
        views=[location_report(self.world),nearby_destinations(self.world),known_places(self.world),plan_route(self.world,'p032'),snapshot(self.world)]
        for view in views:
            if isinstance(view,dict):view.clear()
            else:view.clear()
        self.assertEqual(self.world,before)
        legacy=deepcopy(self.world);legacy.pop('navigation');legacy.pop('navigation_version');before=deepcopy(legacy)
        with self.assertRaises(ValueError):location_report(legacy)
        self.assertEqual(legacy,before)

    def test_rejected_travel_is_atomic_for_all_known_failures(self):
        for destination,mode in [('missing','auto'),('goon.region.r03','auto'),('p001','auto'),('p042','auto'),('n46','auto'),('n31','car'),('home','auto')]:
            with self.subTest(destination=destination,mode=mode):self.rejected(lambda:self.move(destination,mode))
        self.rejected(lambda:execute_command(self.world,'travel',destination='p032',mode=1))

    def test_custody_cannot_be_bypassed(self):
        self.world['cases'].append(dict(id=1,crime='fixture',suspect='Rookie',status='charged',evidence=3))
        self.world['player'].update(arrested=True,custody='pretrial')
        validate(self.world)
        self.rejected(lambda:self.move('p032'))
        advance_day(self.world);self.move('p032');validate(self.world)

    def test_routes_cost_boarding_return_and_reject_distant_journey(self):
        self.move('n13')
        quote=plan_route(self.world,'n31','bus')
        self.assertEqual((quote['cost'],quote['return_cost']),(6,6))
        self.assertTrue(quote['return_fits_today'])
        self.move('n31','bus');self.move('n13','bus')
        self.assertEqual(self.world['navigation']['tu_used'],13)
        self.rejected(lambda:self.move('n40','walk'))

    def test_exact_budget_boundary(self):
        self.world['navigation']['tu_used']=17
        self.move('p032');self.assertEqual(self.world['navigation']['tu_used'],18)
        self.rejected(lambda:self.move('home'))

    def test_public_graph_reachable_but_not_always_within_budget(self):
        self.move('n13')
        for n in range(1,49):
            if n==46:continue
            self.assertGreater(plan_route(self.world,f'n{n:02}')['cost'] if n!=13 else 1,0)
        self.world['navigation']['location_id']='goon.neighborhood.n03'
        quote=plan_route(self.world,'n40')
        self.assertEqual(quote['cost'],17);self.assertEqual(quote['return_cost'],17)
        self.assertFalse(quote['return_fits_today'])
        # Connectivity is not permission to overspend; further remote endpoints exceed 18.
        self.world['navigation']['location_id']='goon.neighborhood.n01'
        self.assertEqual(plan_route(self.world,'n40')['cost'],19)
        self.world['navigation']['tu_used']=0
        self.rejected(lambda:self.move('n40'))

    def test_known_closure_detours_without_hidden_state_leak(self):
        self.move('n13');self.closure()
        quote=plan_route(self.world,'n31','bus');self.assertEqual(quote['cost'],8)
        self.assertNotIn('goon.edge.e06',[leg['edge_id'] for leg in quote['legs']])
        self.move('n31','bus');validate(self.world)

    def test_unknown_closure_commits_safe_prefix_and_survives_resume(self):
        self.move('n13');closure=self.closure(known=False)
        quote=plan_route(self.world,'n31','bus');self.assertEqual(quote['cost'],6)
        before=self.world['navigation']['tu_used'];result=self.move('n31','bus')['result']
        self.assertTrue(result['interrupted']);self.assertEqual(result['arrived'],'goon.neighborhood.n18')
        self.assertEqual(result['tu_cost'],2);self.assertEqual(result['traversed'],['goon.edge.local.r03.06'])
        self.assertEqual(self.world['navigation']['tu_used'],before+2)
        self.assertTrue(self.world['navigation']['closures'][0]['known'])
        self.assertFalse(closure['known']) # transaction replaced nested references
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'career.json';save_career(self.world,path);resumed=load_career(path)
            self.assertEqual(plan_route(resumed,'n31','bus'),plan_route(self.world,'n31','bus'))
            self.assertEqual(resumed,self.world)

    def test_unknown_first_edge_discovery_has_no_phantom_cost(self):
        self.move('n18');self.closure(known=False)
        result=self.move('n31','bus')['result']
        self.assertEqual(result['tu_cost'],0);self.assertEqual(result['origin'],result['arrived'])
        self.assertTrue(result['interrupted'])
        self.assertGreater(plan_route(self.world,'n31','bus')['cost'],3)

    def test_closure_direction_and_mode_are_independent(self):
        self.move('n18');self.closure()
        self.assertEqual(plan_route(self.world,'n23','rail')['cost'],3)
        self.assertGreater(plan_route(self.world,'n23','bus')['cost'],3)
        self.world['navigation']['location_id']='goon.neighborhood.n23'
        self.assertEqual(plan_route(self.world,'n18','bus')['cost'],3)

    def test_isolated_island_has_finite_reopening_without_paid_rescue(self):
        self.world['navigation']['location_id']='goon.neighborhood.n45'
        for i,mode in enumerate(('walk','bus')):self.closure('e15','n45',mode,ident=f'closure.{i}')
        self.world['player']['cash']=0;self.world['actions_used']=3;self.world['navigation']['tu_used']=18
        self.rejected(lambda:self.move('n43'))
        self.assertIn('Saving',location_report(self.world)['help'])
        advance_day(self.world);self.rejected(lambda:self.move('n43'))
        advance_day(self.world);self.move('n43');validate(self.world)

    def test_expired_visit_permission_preserves_departure_but_not_reentry(self):
        self.world['navigation']['location_id']='goon.neighborhood.n43'
        self.world['navigation']['permissions']=['goon.neighborhood.n46']
        self.move('n46');self.world['navigation']['permissions']=[]
        self.move('n43');self.rejected(lambda:self.move('n46'))
        self.rejected(lambda:self.move('p112'))

    def test_one_way_definitions_are_respected(self):
        places,edges=navigation._definitions();edges['goon.edge.e06']['bidirectional']=False
        with patch('navigation._definitions',return_value=(places,edges)):
            self.world['navigation']['location_id']='goon.neighborhood.n18'
            self.assertEqual(plan_route(self.world,'n23','bus')['cost'],3)
            self.world['navigation']['location_id']='goon.neighborhood.n23'
            self.assertGreater(plan_route(self.world,'n18','bus')['cost'],3)

    def test_all_public_destinations_keep_routes_under_reversed_definitions(self):
        expected={n:plan_route(self.world,f'n{n:02}') for n in range(1,49) if n!=46}
        places,edges=navigation._definitions()
        places=dict(reversed(list(places.items())))
        edges=dict(reversed(list(edges.items())))
        for e in edges.values():e['modes']=dict(reversed(list(e['modes'].items())))
        with patch('navigation._definitions',return_value=(places,edges)):
            for n,quote in expected.items():self.assertEqual(plan_route(self.world,f'n{n:02}'),quote)

    def test_daily_reset_is_idempotent_and_loading_never_refreshes(self):
        self.move('p032');advance_day(self.world);self.move('home')
        before=deepcopy(self.world);navigation.begin_day(self.world);gameplay.prepare(self.world)
        self.assertEqual(before,self.world)
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'career.json';save_career(self.world,p)
            self.assertEqual(load_career(p),self.world);self.assertEqual(load_career(p)['navigation']['tu_used'],1)
            self.world['day']+=1 # compatibility with old low-level batch tooling
            save_career(self.world,p);resumed=load_career(p)
            self.assertEqual(resumed['navigation']['tu_used'],1)
            self.assertEqual(resumed['navigation']['tu_day'],1)
            advance_day(resumed);self.assertEqual(resumed['navigation']['tu_used'],0)

    def test_every_historical_generation_loads_without_location_or_income(self):
        fixtures=Path(__file__).parent/'fixtures'
        for path in sorted(fixtures.glob('*.json')):
            raw=json.loads(path.read_text(encoding='utf-8'));world=load_career(path)
            self.assertNotIn('navigation',world)
            for key in ('events','factions','day'):self.assertEqual(raw[key],world[key])
            before=deepcopy(world)
            execute_command(world,'enable_navigation',anchor='n13')
            self.assertIsNone(world['navigation']['location_id']);self.assertIsNone(world['navigation']['home_id'])
            self.assertEqual(world['actions_used'],before['actions_used'])
            with tempfile.TemporaryDirectory() as folder:
                p=Path(folder)/'career.json';save_career(world,p);world=load_career(p)
                self.assertIsNone(world['navigation']['location_id'])
            advance_day(world)
            self.assertEqual(world['navigation']['location_id'],'goon.neighborhood.n13')
            self.assertEqual(world['navigation']['tu_used'],0);validate(world)
            with self.assertRaises(ValueError):execute_command(world,'enable_navigation',anchor='n13')

    def test_legacy_adoption_rejects_nonpublic_anchors(self):
        self.world.pop('navigation');self.world.pop('navigation_version')
        for anchor in ('p031','n46','bad'):
            self.rejected(lambda:execute_command(self.world,'enable_navigation',anchor=anchor))

    def test_malformed_navigation_and_events_are_rejected(self):
        self.move('p032')
        mutations=[lambda w:w.update(navigation_version=True),lambda w:w.update(navigation_version=2),lambda w:w.pop('navigation_version'),
            lambda w:w['navigation'].update(atlas_version=2),lambda w:w['navigation'].update(atlas_fingerprint='missing'),
            lambda w:w['navigation'].update(rules_version=2),lambda w:w['navigation'].update(location_id=[]),
            lambda w:w['navigation'].update(anchor_id=[]),lambda w:w['navigation'].update(home_id=[]),
            lambda w:w['navigation'].update(tu_used=-1),lambda w:w['navigation'].update(tu_used=19),
            lambda w:w['navigation'].update(tu_used=True),lambda w:w['navigation'].update(tu_day=-1),
            lambda w:w['navigation'].update(permissions=['bad']),lambda w:w['navigation'].update(journey_sequence=0),
            lambda w:next(e for e in w['events'] if e['kind']=='travel').update(tu_after=18)]
        for mutate in mutations:
            w=deepcopy(self.world);mutate(w)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError):validate(w)

    def test_unbounded_or_malformed_closures_are_rejected(self):
        self.closure();validate(self.world)
        for key,value in [('end_day',999),('edge_id','missing'),('from_id','goon.neighborhood.n01'),('mode','boat'),('known',1),('start_day',-1)]:
            w=deepcopy(self.world);w['navigation']['closures'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(w)

    def test_saved_travel_history_rejects_fabricated_costs_and_paths(self):
        self.move('n31','bus')
        mutations=[lambda e:e['legs'][0].update(to_id='goon.neighborhood.n40'),
                   lambda e:e['legs'][-1].update(tu=0),lambda e:e.update(discoveries=['fake']),
                   lambda e:e.update(schema_version=2),lambda e:e.update(arrived=e['origin']),
                   lambda e:e.update(command_id=999)]
        for mutate in mutations:
            w=deepcopy(self.world);mutate(next(e for e in w['events'] if e['kind']=='travel'))
            with self.subTest(mutation=mutate),self.assertRaises(ValueError):validate(w)

    def test_failed_save_keeps_previous_location_and_unsaved_world_intact(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'career.json';save_career(self.world,p)
            saved=deepcopy(self.world);self.move('p032');before=deepcopy(self.world)
            with patch('career_persistence.os.replace',side_effect=OSError('fixture disk failure')):
                with self.assertRaises(OSError):save_career(self.world,p)
            self.assertEqual(load_career(p),saved);self.assertEqual(self.world,before)

    def test_changed_or_missing_pinned_atlas_cannot_silently_reset_career(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'career.json';save_career(self.world,p)
            data=json.loads(p.read_text(encoding='utf-8'));data['navigation']['atlas_fingerprint']='different'
            p.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'pinned local atlas'):load_career(p)
        location_registry._catalog.cache_clear()
        try:
            with patch('location_registry.ATLAS_PATH',Path('missing_atlas_fixture.json')):
                with self.assertRaisesRegex(ValueError,'required local atlas'):location_registry.load()
        finally:
            location_registry._catalog.cache_clear()

    def test_multi_day_replay_ordering_and_disk_resume_preserve_economy(self):
        a,b=create_career(17),create_career(17);baseline=create_career(17)
        for w in (a,b,baseline):execute_command(w,'join',faction='Harbor Syndicate')
        original=navigation._definitions
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'career.json'
            for day in range(40):
                for w in (a,b):
                    def reversed_definitions():
                        places,edges=original()
                        return dict(reversed(list(places.items()))),dict(reversed(list(edges.items())))
                    with patch('navigation._definitions',side_effect=reversed_definitions if w is b else original):
                        self.move('p032',world=w);execute_command(w,'job',kind='courier');self.move('home',world=w);advance_day(w)
                execute_command(baseline,'job',kind='courier');advance_day(baseline)
                if day%7==0:save_career(b,p);b=load_career(p)
                self.assertEqual(a,b);validate(a)
                for key in ('factions','districts','cases','player','job_attempts'):
                    self.assertEqual(a[key],baseline[key])
            self.assertEqual(a['day'],40)

    def test_fresh_process_hashseed_and_global_rng_isolation(self):
        state=random.getstate();self.move('p032');self.assertEqual(random.getstate(),state)
        code='import json,hashlib;from game_service import *;w=create_career(17);execute_command(w,"travel",destination="n31",mode="auto");advance_day(w);execute_command(w,"travel",destination="home",mode="auto");print(hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest())'
        outputs=[subprocess.check_output([sys.executable,'-B','-c',code],cwd=Path(__file__).resolve().parents[1],env=dict(os.environ,PYTHONHASHSEED=seed),text=True) for seed in ('0','42')]
        self.assertEqual(outputs[0],outputs[1])

    def test_cli_home_work_return_and_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'career.json';out=io.StringIO()
            commands=['look','nearby','route p032','travel p032','look','join 1','job courier','travel home','wait','quit']
            with patch('sys.argv',['gameplay.py','--save',str(path)]),patch('builtins.input',side_effect=commands),contextlib.redirect_stdout(out):gameplay.main()
            self.assertIn('East Side Housing Cooperative',out.getvalue());self.assertIn('Uptown General Store',out.getvalue())
            w=load_career(path);self.assertEqual(w['day'],1);self.assertEqual(w['job_attempts'],1)
            self.assertEqual(w['navigation']['location_id'],'goon.poi.p031');self.assertEqual(w['navigation']['tu_used'],0)
            with patch('sys.argv',['gameplay.py','--load','--save',str(path)]),patch('builtins.input',side_effect=['look','quit']),contextlib.redirect_stdout(io.StringIO()):gameplay.main()
            self.assertEqual(load_career(path),w)


if __name__ == '__main__':
    unittest.main()
