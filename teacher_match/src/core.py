def match_teachers_to_principals(data):
    principal_queues_by_id = {}
    if data:
        for teacher in (data.get('teachers') or []):
            if teacher.get('credentials') == 'Active':
                for principal in (data.get('principals') or []):
                    if principal.get('location') == teacher.get('geography'):
                        for role in (principal.get('openRoles') or []):
                            if role.get('grade') in teacher.get('grades') and role.get('subject') in teacher.get(
                                    'subjects'):
                                principal_queue = principal_queues_by_id.setdefault(principal.get('id'),
                                                                                    empty_principal_queue(
                                                                                        principal.get('id')))
                                principal_queue['principalQueue'].append(teacher.get('id'))
                                break
    return {'queues': list(principal_queues_by_id.values())}


def empty_principal_queue(principal_id):
    return {'principalId': principal_id,
            'principalQueue': []}
