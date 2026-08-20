import csv
from io import TextIOWrapper

REQUIRED_HEADERS = ['employee_id','employee_name','email','manager_id','manager_email','department']

class ParseError(Exception):
    pass


def _normalize(row):
    return {
        'employee_id': row.get('employee_id','').strip(),
        'employee_name': row.get('employee_name','').strip(),
        'email': row.get('email','').strip().lower(),
        'manager_id': row.get('manager_id','').strip(),
        'manager_email': row.get('manager_email','').strip().lower(),
        'department': row.get('department','').strip(),
    }


def parse_csv(file_obj):
    try:
        text = TextIOWrapper(file_obj, encoding='utf-8-sig')
    except Exception:
        raise ParseError('Unable to read uploaded file as text')

    reader = csv.DictReader(text)
    headers = [h.strip() for h in reader.fieldnames] if reader.fieldnames else []
    for h in REQUIRED_HEADERS:
        if h not in headers:
            raise ParseError(f'Missing required header: {h}')

    rows = []
    for i, raw in enumerate(reader, start=2):
        norm = _normalize(raw)
        rows.append({'source_row': i, 'raw': raw, 'normalized': norm, 'errors': [], 'error_codes': []})

    # Identity validation
    id_map = {}
    email_map = {}
    dup_ids = set()
    dup_emails = set()

    for r in rows:
        nid = r['normalized']['employee_id']
        email = r['normalized']['email']
        if not nid:
            r['errors'].append('missing employee_id')
            r['error_codes'].append('missing_employee_id')
        if not email:
            r['errors'].append('missing email')
            r['error_codes'].append('missing_email')
        if nid:
            if nid in id_map:
                dup_ids.add(nid)
            else:
                id_map[nid] = r
        if email:
            if email in email_map:
                dup_emails.add(email)
            else:
                email_map[email] = r

    for r in rows:
        nid = r['normalized']['employee_id']
        email = r['normalized']['email']
        if nid in dup_ids:
            r['errors'].append('duplicate employee_id')
            r['error_codes'].append('duplicate_employee_id')
        if email in dup_emails:
            r['errors'].append('duplicate email')
            r['error_codes'].append('duplicate_email')

    # Accepted employees: those without identity errors
    accepted = [r for r in rows if not any('duplicate' in e or 'missing' in e for e in r['errors'])]

    # Manager lookup
    for r in accepted:
        mid = r['normalized']['manager_id']
        memail = r['normalized']['manager_email']
        if not mid and not memail:
            r['manager'] = None
            r['is_root'] = True
            continue
        r['is_root'] = False
        manager = None
        if mid:
            manager = id_map.get(mid)
            if not manager:
                r['errors'].append(f'manager_id {mid} not found')
                r['error_codes'].append('manager_id_not_found')
        if memail:
            manager_by_email = email_map.get(memail)
            if not manager_by_email:
                r['errors'].append(f'manager_email {memail} not found')
                r['error_codes'].append('manager_email_not_found')
            # If both id and email provided, ensure they point to same employee.
            if mid and manager:
                mgr_email = manager['normalized'].get('email')
                if memail and mgr_email and mgr_email != memail:
                    r['errors'].append('manager id/email mismatch')
                    r['error_codes'].append('manager_id_email_mismatch')
            if not mid and manager_by_email:
                manager = manager_by_email
        if manager and manager is r:
            r['errors'].append('employee manages themselves')
            r['error_codes'].append('employee_manages_self')
            r['manager'] = None
        elif manager:
            r['manager'] = manager['normalized']['employee_id']
        else:
            r['manager'] = None

    # Build reporting relationships for accepted rows with valid manager references
    employee_ids = {r['normalized']['employee_id'] for r in accepted}
    edges = {}
    for r in accepted:
        eid = r['normalized']['employee_id']
        mid = r.get('manager')
        if mid and mid in employee_ids and not any(c.startswith('manager_') or c=='manager_id_email_mismatch' for c in r['error_codes']):
            edges[eid] = mid

    # Detect cycles
    visited = {}
    in_cycle = set()

    def dfs(node, stack):
        if node in visited:
            return
        visited[node] = True
        nxt = edges.get(node)
        if not nxt:
            return
        if nxt in stack:
            # cycle found
            idx = stack.index(nxt)
            cyc = stack[idx:]+[nxt]
            in_cycle.update(cyc)
            return
        dfs(nxt, stack+[nxt])

    for n in employee_ids:
        if n not in visited:
            dfs(n, [n])

    # Annotate rows
    for r in accepted:
        eid = r['normalized']['employee_id']
        r['in_cycle'] = eid in in_cycle

    # Manager direct-report counts
    manager_counts = {}
    for reporter, mgr in edges.items():
        manager_counts[mgr] = manager_counts.get(mgr, 0) + 1

    managers = []
    for mid, count in manager_counts.items():
        mrow = id_map.get(mid)
        if mrow:
            managers.append({'manager_id': mid, 'manager_name': mrow['normalized']['employee_name'], 'direct_reports': count})

    roots = [r for r in accepted if r.get('is_root') and not r.get('errors')]

    return {
        'total_rows': len(rows),
        'rows': rows,
        'accepted': accepted,
        'errors': [r for r in rows if r['errors']],
        'roots': roots,
        'managers': managers,
        'cycles': list(in_cycle),
    }
