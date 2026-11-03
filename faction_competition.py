"""M013 bounded daily economy and strategic operations, independent of content."""
from simulation import event, remember
from territory import capture


def active(world):
    return 'competition' in world and world['day'] >= world['competition']['activation_day']


def _participants(world):
    return sorted(world['competition']['factions'])


def _profile(world, faction):
    profile_id = world['competition']['factions'][faction]
    return profile_id, world['competition']['profiles'][profile_id]


def _holdings(world, faction):
    return [(name, d) for name, d in sorted(world['districts'].items()) if d['owner'] == faction]


def economy(world):
    if not active(world) or world['economy_last_day'] >= world['day']:
        return []
    emitted = []
    for name, district in sorted(world['districts'].items()):
        owner = district['owner']
        if owner not in world['competition']['factions']:
            continue
        profile_id, profile = _profile(world, owner)
        treasury = world['factions'][owner]
        before = treasury['cash']
        gross = max(1, district['wealth'] // 15) * profile['revenue_percent'] // 100
        income = min(gross, max(0, profile['treasury_cap'] - before))
        treasury['cash'] += income
        emitted.append(event(world, 'economy', f'{owner} earned ${income} from {name}.',
                             district=name, faction=owner, profile=profile_id, income=income,
                             gross_income=gross, cash_before=before, cash_after=treasury['cash'],
                             cause='district_income'))
        # Pressure weakens control but cannot give a resource-free ownership transfer.
        before_control = district['control']
        pressure = 1 + (world['day'] + len(name)) % 3
        district['control'] = max(1, before_control - pressure) if before_control else 0
        emitted.append(event(world, 'territory_pressure', f'{name} lost {before_control - district["control"]} control to local pressure.',
                             district=name, faction=owner, control_before=before_control,
                             control_after=district['control'], cause='local_pressure'))
    for faction in _participants(world):
        profile_id, profile = _profile(world, faction)
        data = world['factions'][faction]
        before_cash, before_power = data['cash'], data['power']
        holdings = len(_holdings(world, faction))
        bill = profile['operating_cost'] + holdings * profile['holding_cost'] + data['power'] // profile['upkeep_divisor']
        paid = min(data['cash'], bill)
        data['cash'] -= paid
        data['power'] = min(100, data['power'] + 1) if paid == bill else max(0, data['power'] - 1)
        emitted.append(event(world, 'faction_economy', f'{faction} paid ${paid}/${bill} upkeep; power {data["power"]}.',
                             faction=faction, profile=profile_id, holdings=holdings, upkeep=bill, paid=paid,
                             cash_before=before_cash, cash_after=data['cash'], power_before=before_power,
                             power_after=data['power'], cause='organizational_upkeep'))
    world['economy_last_day'] = world['day']
    return emitted


def assess(world, faction, pressure=None):
    profile_id, profile = _profile(world, faction)
    data = world['factions'][faction]
    owned = _holdings(world, faction)
    rivals = [(name, d) for name, d in sorted(world['districts'].items())
              if d['owner'] in world['competition']['factions'] and d['owner'] != faction]
    pressure = pressure or {}
    weak = min(owned, key=lambda x: (x[1]['control'] - pressure.get(x[0], 0), x[0])) if owned else None
    target = min(rivals, key=lambda x: (x[1]['control'], -x[1]['wealth'], x[0])) if rivals else None
    cash, power = data['cash'], data['power']
    district = None
    if power < profile['min_attack_power']:
        objective = 'regroup' if cash >= profile['recruitment_cost'] else 'recover'
        reason = f'power={power} below operating strength {profile["min_attack_power"]}'
    elif weak and weak[1]['control'] - pressure.get(weak[0], 0) <= profile['defense_threshold'] and cash >= profile['defense_cost']:
        objective, district = 'defend', weak[0]
        reason = f'control={weak[1]["control"]}, player_pressure={pressure.get(district, 0)}, defense threshold={profile["defense_threshold"]}'
    elif cash < profile['attack_reserve']:
        objective, reason = 'recover', f'treasury=${cash} below operating reserve ${profile["attack_reserve"]}'
    elif target:
        objective, district = 'expand', target[0]
        reason = f'funded expansion: target control={target[1]["control"]}, power={power}'
    elif weak and weak[1]['control'] < profile['consolidation_threshold'] and cash >= profile['defense_cost']:
        objective, district = 'consolidate', weak[0]
        reason = f'consolidate control below {profile["consolidation_threshold"]}'
    elif power < 100 and cash >= profile['recruitment_cost']:
        objective, reason = 'regroup', 'funded organizational recruitment'
    else:
        objective, reason = 'recover', 'preserve resources within recovery capacity'
    return {'faction': faction, 'objective': objective, 'district': district,
            'reason': reason, 'profile': profile_id, 'treasury': cash, 'power': power,
            'owned_count': len(owned), 'day': world['day']}


def warfare(world):
    if not active(world) or world['warfare_last_day'] >= world['day']:
        return []
    names = _participants(world)
    offset = (world['seed'] + world['day']) % len(names)
    emitted = []
    for faction in names[offset:] + names[:offset]:
        profile_id, profile = _profile(world, faction)
        data = world['factions'][faction]
        stored = world.get('faction_strategy', {}).get(faction)
        plan = stored if isinstance(stored, dict) and stored.get('day') == world['day'] else assess(world, faction)
        objective, target = plan['objective'], plan.get('district')
        details = {'faction': faction, 'profile': profile_id, 'district': target,
                   'strategy_objective': objective, 'strategy_reason': plan['reason'],
                   'cash_before': data['cash'], 'power_before': data['power'], 'captured': False}
        reason = None
        if stored is not plan:
            details.update(fallback_reason='no current-day plan; reassessed from current resources',
                           planned_objective=stored.get('objective') if isinstance(stored, dict) else None)
        if plan.get('profile') != profile_id:
            reason = 'economic profile changed after planning'
        elif objective == 'recover':
            gain = min(profile['recovery_income'], max(0, min(profile['recovery_cap'], profile['treasury_cap']) - data['cash']))
            if gain == 0 and data['power'] == 100:
                reason = 'recovery capacity is already full'
            else:
                data['cash'] += gain
                data['power'] = min(100, data['power'] + profile['recovery_power'])
                details.update(action='recover', cost=0, income=gain, cause='time_spent_recovering')
        elif objective == 'regroup':
            if data['cash'] < profile['recruitment_cost'] or data['power'] >= 100:
                reason = 'recruitment funding or capacity is no longer available'
            else:
                data['cash'] -= profile['recruitment_cost']
                data['power'] = min(100, data['power'] + profile['recruitment_gain'])
                details.update(action='regroup', cost=profile['recruitment_cost'], cause='paid_recruitment')
        elif objective in ('defend', 'consolidate', 'expand'):
            district = world['districts'].get(target)
            cost = profile['attack_cost'] if objective == 'expand' else profile['defense_cost']
            if district is None or (objective == 'expand' and (district['owner'] == faction or district['owner'] not in names)):
                reason = 'planned expansion target is no longer available'
            elif objective != 'expand' and district['owner'] != faction:
                reason = 'planned defense target is no longer owned'
            elif data['cash'] < cost or (objective == 'expand' and data['power'] < profile['min_attack_power']):
                reason = 'planned operation no longer has funding or operating strength'
            elif objective != 'expand' and district['control'] >= 100:
                reason = 'planned defense has no control capacity'
            else:
                before = district['control']
                data['cash'] -= cost
                details.update(cost=cost, control_before=before)
                if objective == 'expand':
                    owner = district['owner']
                    defender = world['factions'][owner]
                    defender_power = defender['power']
                    damage = min(before, profile['attack_base'] + data['power'] // 25)
                    district['control'] -= damage
                    data['power'] = max(0, data['power'] - 1)
                    defender['power'] = max(0, defender['power'] - 2)
                    details.update(action='attack', previous_owner=owner, control_delta=-damage,
                                   defender_power_before=defender_power, defender_power_after=defender['power'],
                                   cause='faction_offensive')
                    if district['control'] == 0:
                        details.update(capture(world, target, faction), captured=True)
                else:
                    gain = min(100 - before, profile['defense_base'] + data['power'] // 25)
                    if objective == 'consolidate':
                        gain = max(1, gain // 2)
                        data['power'] = min(100, data['power'] + profile['recruitment_gain'] // 2)
                    district['control'] += gain
                    details.update(action=objective, control_delta=gain, cause='faction_defense')
                details['control_after'] = district['control']
        else:
            reason = 'planned objective is unsupported'
        if reason:
            details.update(action='hold', cost=0, cause='strategy_fallback',
                           strategy_objective='hold', strategy_reason=reason,
                           planned_objective=objective, fallback_reason=reason)
        details.update(cash_after=data['cash'], power_after=data['power'])
        message = f'{faction}: {details["action"]}' + (f' at {target}' if target else '') + (f'; {reason}.' if reason else '.')
        actor = next((name for name, person in sorted(world['people'].items()) if person['faction'] == faction), None)
        details['npc'] = actor
        if actor:
            remember(world, actor, message)
        emitted.append(event(world, 'faction_warfare', message, **details))
    world['warfare_last_day'] = world['day']
    return emitted
