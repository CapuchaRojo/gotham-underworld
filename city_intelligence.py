"""M010: read-only, deterministic intelligence over documented city state."""
from copy import deepcopy
from city_economy import GANGS

TERRITORY_CAUSES = {'control_exhausted', 'faction_offensive'}


def rankings(world):
    """Rank gangs by holdings, aggregate control, power and treasury."""
    rows = []
    for faction in GANGS:
        if faction not in world.get('factions', {}):
            continue
        owned = [d for d in world.get('districts', {}).values() if d['owner'] == faction]
        stats = world['factions'][faction]
        rows.append({'faction': faction, 'districts': len(owned),
                     'control': sum(d['control'] for d in owned),
                     'power': stats['power'], 'cash': stats['cash']})
    return sorted(rows, key=lambda r: (-r['districts'], -r['control'],
                                        -r['power'], -r['cash'], r['faction']))


def territory_history(world, limit=10):
    """Only actual captures or ownership transfers, not mere attacks."""
    if limit < 0:
        raise ValueError('limit must be nonnegative')
    transfers = []
    for item in world.get('events', []):
        if item.get('kind') == 'territory' and item.get('cause') == 'control_exhausted':
            transfers.append(item)
        elif item.get('kind') == 'faction_warfare' and item.get('captured') is True:
            transfers.append(item)
        elif item.get('kind') == 'district_mission' and item.get('captured') is True:
            transfers.append(item)
    return deepcopy(transfers[-limit:]) if limit else []


def player_influence(world):
    """Attribute only explicit player events, never NPC/AI warfare."""
    player = world.get('player', {})
    faction = player.get('faction')
    missions = [e for e in world.get('events', [])
                if e.get('kind') == 'district_mission' and e.get('cause') == 'player_district_mission']
    jobs = [e for e in world.get('events', [])
            if e.get('kind') == 'job' and e.get('cause') == 'player_job']
    captures = sum(e.get('captured') is True for e in missions)
    expansion = sum(1 for e in missions if e.get('mission') == 'expand')
    return {'faction': faction, 'missions': len(missions), 'expansions': expansion,
            'captures': captures, 'jobs': len(jobs),
            'successful_jobs': sum(e.get('success') is True for e in jobs),
            'reputation': player.get('reputation', {}).get(faction, 0) if faction else 0}


def briefing(world, day=None):
    """Summarize recorded events for a day; no forecasts or hidden knowledge."""
    if day is None:
        day = world['day']
    if not isinstance(day, int) or day < 0 or day > world['day']:
        raise ValueError('day must be an elapsed nonnegative day')
    events = [e for e in world.get('events', []) if e.get('day') == day]
    kinds = ('faction_strategy', 'faction_warfare', 'territory', 'district_mission',
             'npc_action', 'arrest', 'court', 'sentencing')
    highlights = [e['message'] for e in events if e.get('kind') in kinds]
    income = sum(e.get('income', 0) for e in events if e.get('kind') == 'economy')
    return {'day': day, 'event_count': len(events), 'income': income,
            'highlights': highlights}


def dashboard(world):
    """Snapshot only: reading it must not prepare or mutate saves."""
    return {'day': world['day'], 'rankings': rankings(world),
            'territory_history': territory_history(world),
            'player_influence': player_influence(world),
            'briefing': briefing(world)}
