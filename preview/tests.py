import io
from django.test import TestCase
from .parser import parse_csv

class ParserTests(TestCase):
    def test_normalization_and_duplicates(self):
        csv_data = """employee_id,employee_name,email,manager_id,manager_email,department
A,Name,Email@EXAMPLE.com,,,Dept
B,Name2,email@example.com,,,Dept
"""
        f = io.BytesIO(csv_data.encode('utf-8'))
        result = parse_csv(f)
        self.assertEqual(result['total_rows'], 2)
        # emails should be lowercased
        emails = [r['normalized']['email'] for r in result['rows']]
        self.assertIn('email@example.com', emails)

    def test_cycle_detection(self):
        csv_data = """employee_id,employee_name,email,manager_id,manager_email,department
A,One,a@e.com,B,,Dept
B,Two,b@e.com,C,,Dept
C,Three,c@e.com,A,,Dept
D,Four,d@e.com,,,Dept
"""
        f = io.BytesIO(csv_data.encode('utf-8'))
        result = parse_csv(f)
        self.assertIn('A', result['cycles'])
        self.assertIn('B', result['cycles'])
        self.assertIn('C', result['cycles'])
        self.assertNotIn('D', result['cycles'])

    def test_duplicate_id_email(self):
        csv_data = """employee_id,employee_name,email,manager_id,manager_email,department
X,One,x@example.com,,,Dept
X,Two,x2@example.com,,,Dept
Y,Three,x@example.com,,,Dept
"""
        f = io.BytesIO(csv_data.encode('utf-8'))
        result = parse_csv(f)
        # duplicate employee_id X should flag both rows
        dup_rows = [r for r in result['rows'] if 'duplicate_employee_id' in r.get('error_codes',[])]
        self.assertTrue(any(r['normalized']['employee_id']=='X' for r in dup_rows))
        # duplicate email should flag both rows that share email
        self.assertTrue(any(r['normalized']['email']=='x@example.com' and 'duplicate_email' in r.get('error_codes',[]) for r in result['rows']))

    def test_manager_conflict_and_missing_manager(self):
        csv_data = """employee_id,employee_name,email,manager_id,manager_email,department
M1,A,m1@e.com,M2,m2@e.com,Dept
M2,B,m2@e.com,,,Dept
M3,C,m3@e.com,M9,,Dept
"""
        f = io.BytesIO(csv_data.encode('utf-8'))
        result = parse_csv(f)
        # first row should be fine (manager exists)
        m1 = next(r for r in result['rows'] if r['normalized']['employee_id']=='M1')
        self.assertFalse(any(c.startswith('manager_') for c in m1.get('error_codes',[])))
        # M3 should have manager_id not found
        m3 = next(r for r in result['rows'] if r['normalized']['employee_id']=='M3')
        self.assertTrue('manager_id_not_found' in m3.get('error_codes',[]))

    def test_missing_required_header_raises(self):
        csv_data = """employee_id,employee_name,email,manager_id,department
A,One,a@e.com,,Dept
"""
        f = io.BytesIO(csv_data.encode('utf-8'))
        with self.assertRaises(Exception):
            parse_csv(f)

    def test_bom_and_whitespace_handling(self):
        # include BOM and extra whitespace
        csv_data = '\ufeffemployee_id,employee_name,email,manager_id,manager_email,department\n  Z , Zoe , Z@E.COM , , , Team\n'
        f = io.BytesIO(csv_data.encode('utf-8'))
        result = parse_csv(f)
        z = result['rows'][0]
        self.assertEqual(z['normalized']['employee_id'], 'Z')
        self.assertEqual(z['normalized']['email'], 'z@e.com')
        self.assertEqual(z['error_codes'], [])
    def test_error_codes_present_for_conflict(self):
        csv_data = """employee_id,employee_name,email,manager_id,manager_email,department
P1,One,p1@e.com,P2,px@e.com,Dept
P2,Two,p2@e.com,,,Dept
"""
        f = io.BytesIO(csv_data.encode('utf-8'))
        result = parse_csv(f)
        p1 = next(r for r in result['rows'] if r['normalized']['employee_id']=='P1')
        self.assertIn('manager_id_email_mismatch', p1.get('error_codes',[]))
