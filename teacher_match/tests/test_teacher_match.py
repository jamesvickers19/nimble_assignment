import os
import unittest

from teacher_match.src.core import match_teachers_to_principals
from teacher_match.src.process_file import process_file
from teacher_match.src.utils import load_json

test_dir = os.path.dirname(os.path.abspath(__file__))

matching_geography = "Albuquerque"
matching_subject = "History"
matching_grade = '5th grades'


def should_match_principal(principal_id):
    return {'id': principal_id, 'name': 'a teacher', 'location': matching_geography,
            'openRoles': [{'subject': matching_subject, 'grade': matching_grade}]}


def should_match_teacher(teacher_id):
    return {'id': teacher_id, 'name': 'a principal', 'geography': matching_geography,
            'credentials': 'Active',
            'grades': [matching_grade],
            'subjects': [matching_subject]}


# Don't fail tests because ordering differs, not semantically important.
# To do that, sort each principalQueue value and sort the overall queues by principalId.
def to_order_independent(principal_queues):
    if 'queues' in principal_queues:
        for q in (principal_queues.get('queues') or []):
            if 'principalQueue' in q:
                q['principalQueue'].sort()
        principal_queues['queues'] = sorted(principal_queues['queues'], key=lambda d: d['principalId'])


class TeacherMatchTest(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual({'queues': []}, match_teachers_to_principals({}))

    def test_none_input(self):
        self.assertEqual({'queues': []}, match_teachers_to_principals(None))

    def exercise_match_teachers_to_principals(self, teachers, principals, expected_principal_queues, msg=None):
        expected = {'queues': expected_principal_queues}
        to_order_independent(expected)
        actual_principal_queues = match_teachers_to_principals({'teachers': teachers, 'principals': principals})
        to_order_independent(actual_principal_queues)
        self.assertEqual(expected, actual_principal_queues, msg=msg)

    def test_no_teachers_or_principals(self):
        self.exercise_match_teachers_to_principals(teachers=[], principals=[], expected_principal_queues=[])

    def test_no_teachers(self):
        self.exercise_match_teachers_to_principals(teachers=[],
                                                   principals=[should_match_principal(123)],
                                                   expected_principal_queues=[])

    def test_no_principals(self):
        self.exercise_match_teachers_to_principals(teachers=[should_match_teacher(123)],
                                                   principals=[],
                                                   expected_principal_queues=[])

    def test_teacher_lacking_credentials(self):
        teacher_id = 567
        principal_id = 789
        principal = should_match_principal(principal_id)
        for invalid_credential in ['Expired', 'No credentials']:
            teacher = should_match_teacher(teacher_id)
            teacher['credentials'] = invalid_credential
            msg = f"Teacher should not match because credentials are '{invalid_credential}'"
            self.exercise_match_teachers_to_principals(teachers=[teacher],
                                                       principals=[principal],
                                                       expected_principal_queues=[],
                                                       msg=msg)

    def test_geography_mismatch(self):
        teacher_id = 3
        principal_id = 4
        teacher = should_match_teacher(teacher_id)
        teacher['geography'] = 'Not' + matching_geography
        principal = should_match_principal(principal_id)
        self.exercise_match_teachers_to_principals(teachers=[teacher],
                                                   principals=[principal],
                                                   expected_principal_queues=[])

    def test_grade_mismatch(self):
        teacher_id = 12345
        principal_id = 234
        teacher = should_match_teacher(teacher_id)
        principal = should_match_principal(principal_id)
        teacher['grades'] = ['Not' + matching_grade]
        self.exercise_match_teachers_to_principals(teachers=[teacher],
                                                   principals=[principal],
                                                   expected_principal_queues=[])

    def test_subject_mismatch(self):
        teacher_id = 12345
        principal_id = 234
        teacher = should_match_teacher(teacher_id)
        principal = should_match_principal(principal_id)
        teacher['subjects'] = ['Not' + matching_subject]
        self.exercise_match_teachers_to_principals(teachers=[teacher],
                                                   principals=[principal],
                                                   expected_principal_queues=[])

    def test_single_match(self):
        teacher_id = 1
        principal_id = 2
        teacher = should_match_teacher(teacher_id)
        principal = should_match_principal(principal_id)
        self.exercise_match_teachers_to_principals(teachers=[teacher],
                                                   principals=[principal],
                                                   expected_principal_queues=[{'principalId': principal_id,
                                                                               'principalQueue': [teacher_id]}])

    def test_teachers_matched_to_multiple_principals(self):
        geography = "Philly"
        teacher_id_1 = 123
        teacher_1 = {
            'id': teacher_id_1, 'name': 'a teacher 1', 'geography': geography,
            'credentials': 'Active',
            'grades': ["2nd grades", "3rd grades"],
            'subjects': ["Science", "Special Education"]}
        teacher_id_2 = 5678
        teacher_2 = {
            'id': teacher_id_2, 'name': 'a teacher 2', 'geography': geography,
            'credentials': 'Active',
            'grades': ["4th grades", "5th grades"],
            'subjects': ["History", "Math"]}
        teacher_id_3 = 593828392
        not_matched_teacher = {
            'id': teacher_id_3, 'name': 'a not matched teacher', 'geography': geography,
            'credentials': 'Active',
            'grades': ["4th grades", "5th grades"],
            'subjects': ["Special Education", "English"]}
        principal_id_1 = 12131431
        principal_1 = {'id': principal_id_1, 'name': 'a principal 1', 'location': geography,
                       'openRoles': [{'subject': "Science", 'grade': "2nd grades"},  # matches teacher_1
                                     {'subject': "History", 'grade': "Kindergarten"},
                                     {'subject': "Math", 'grade': "4th grades"}  # matches teacher_2
                                     ]}
        principal_id_2 = 569829382
        principal_2 = {'id': principal_id_2, 'name': 'a principal 2', 'location': geography,
                       'openRoles': [{'subject': "English", 'grade': "2nd grades"},
                                     {'subject': "Special Education", 'grade': "2nd grades"},  # matches teacher_1
                                     {'subject': "History", 'grade': "5th grades"}  # matches teacher_2
                                     ]}
        # orders of things purposely odd, intentionally doesn't matter in tests.
        expected = [{'principalId': principal_id_2, 'principalQueue': [teacher_id_2, teacher_id_1]},
                    {'principalId': principal_id_1, 'principalQueue': [teacher_id_1, teacher_id_2]}]
        self.exercise_match_teachers_to_principals(teachers=[teacher_2, teacher_1, not_matched_teacher],
                                                   principals=[principal_1, principal_2],
                                                   expected_principal_queues=expected)

    # This test exercises any examples found in the 'examples' folder;
    # to make a new example, add a new folder (named as you wish) in there with input.json (input file) and
    # expected_output.json (expected output file).
    # Other files can be added to that directory for e.g. documentation and will be ignored by the test.
    def test_process_file_on_examples(self):
        base_dir = 'examples'
        for possible_dir in os.listdir(os.path.join(test_dir, base_dir)):
            example_dir = os.path.join(base_dir, possible_dir)
            if os.path.isdir(example_dir):
                input_file = os.path.join(example_dir, 'input.json')
                expected_output_file = os.path.join(example_dir, 'expected_output.json')
                if os.path.exists(input_file) and os.path.exists(expected_output_file):
                    print(
                        f"Found test example: input file = {input_file}, expected output file = {expected_output_file}")
                    expected = load_json(expected_output_file)
                    created_output_file = expected_output_file + '_created'
                    process_file(input_file, created_output_file)
                    self.assertTrue(os.path.exists(created_output_file),
                                    f"Expected specified output file {created_output_file} to exist")
                    created_file_contents = load_json(created_output_file)
                    to_order_independent(expected)
                    to_order_independent(created_file_contents)
                    self.assertEqual(expected,
                                     created_file_contents,
                                     f"Created output file {created_output_file} has expected contents")
                    os.remove(created_output_file)


if __name__ == '__main__':
    unittest.main()
