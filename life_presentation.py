"""Pure CLI formatting for detached reports; stable IDs remain interface-neutral."""


def render_choice(report):
    lines = [f'{report["speaker"]} | {report["title"]}', report['situation'],
             f'{report["id"]} | days {report["open_day"]}-{report["expires_day"] - 1} | {report["state"]}']
    letters = {}
    for index, option in enumerate(report['options']):
        letter = chr(65 + index) if index < 26 else str(index + 1)
        letters[letter] = option['id']
        lines.append(f'{letter}. {option["label"]} [{option["id"]}; {option["action_cost"]} action(s)]')
        lines.append('   ' + option['tradeoff'])
        if option['availability'] != 'available':
            lines.append('   Unavailable: ' + option['reason'])
    if report['promise']:
        p = report['promise']
        lines.append(f'Personal promise: {p["status"]}; deadline before day {p["due_day"]}.')
    if report['selection']:
        lines.append('Recorded outcome: ' + report['selection']['outcome']['feedback'])
    return '\n'.join(lines), letters


def render_life(report):
    if not report['enabled']:
        return 'DAILY LIFE | Not enrolled\n' + report['terms'] + '\nVisit p031/n13 and use settle_in to accept these terms.'
    housing = report['housing']
    lines = [f'DAILY LIFE | Day {report["day"]} | cash ${report["cash"]} | home {report["home_id"]}',
        f'Room: {report["status"]}; next review day {housing["next_due_day"]}; prepaid ${housing["prepaid"]}; unpaid ${housing["arrears"]}.']
    if report['pending']:
        lines.append(f'Opportunities activate on day {report["activation_day"]}, after an explicit wait.')
    for p in report['promises']:
        if p['status'] == 'pending':
            lines.append(f'Promise {p["id"]}: due before day {p["due_day"]}.')
    lines.append('Thought: ' + report['monologue'])
    for tx in report['transactions'][-5:]:
        lines.append(f'Day {tx["day"]}: {tx["cause"]} ${tx["amount"]:+}; cash ${tx["after"]} [{tx["id"]}]')
    if 'help' in report:
        lines.append(report['help'])
    return '\n'.join(lines)


def render_contacts(reports):
    lines = []
    for person in reports:
        lines.extend((f'{person["name"]} [{person["id"]}] | standing {person["standing"]}',
                      person['role'] + ': ' + person['personality'], 'Needs: ' + person['need'],
                      'Known scope: ' + person['knowledge']))
        for memory in person['memories'][-3:]:
            lines.append(f'  Day {memory["day"]}: {memory["fact"].replace("_", " ")} [{memory["source_id"]}]')
    return '\n'.join(lines)
