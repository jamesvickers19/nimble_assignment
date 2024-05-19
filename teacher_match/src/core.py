"""
Builds a lookup like so, for matching teachers to principals:
{  "Philly": {
      "1st grades": {
        "subject": principal_ids_array
      },
      "2nd grades": {
         "subject": principal_ids_array
      }
}
"""


def build_open_role_lookup(principals):
    lookup = {}
    for p in principals or []:
        by_location = lookup.setdefault(p.get('location'), {})
        for role in (p.get('openRoles') or []):
            by_grade = by_location.setdefault(role.get('grade'), {})
            by_subject = by_grade.setdefault(role.get('subject'), [])
            by_subject.append(p.get('id'))
    return lookup


def match_teachers_to_principals(data):
    principal_queues_by_id = {}
    if data:
        open_role_lookup = build_open_role_lookup(data.get('principals'))
        for teacher in data.get('teachers') or []:
            if teacher.get('credentials') == 'Active':
                already_matched_principal_ids = set()
                geography = teacher.get('geography')
                for grade in teacher.get('grades') or []:
                    for subject in teacher.get('subjects') or []:
                        matching_principal_ids = open_role_lookup.get(geography, {}).get(grade, {}).get(subject) or []
                        for principal_id in set(matching_principal_ids).difference(already_matched_principal_ids):
                            principal_queue = principal_queues_by_id.setdefault(principal_id,
                                                                                empty_principal_queue(
                                                                                    principal_id))
                            principal_queue['principalQueue'].append(teacher.get('id'))
                            already_matched_principal_ids.add(principal_id)
    return {'queues': list(principal_queues_by_id.values())}


def empty_principal_queue(principal_id):
    return {'principalId': principal_id,
            'principalQueue': []}
