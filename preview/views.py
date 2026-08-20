from django.shortcuts import render
from django.http import HttpResponseBadRequest
from .parser import parse_csv, ParseError
from django.http import HttpResponse
import csv


def upload_view(request):
    if request.method == 'POST':
        f = request.FILES.get('file')
        if not f:
            return HttpResponseBadRequest('No file uploaded')
        try:
            result = parse_csv(f.file)
        except ParseError as e:
            return render(request, 'upload.html', {'error': str(e)})
        # Optional UI filters from the form
        dept = request.POST.get('filter_department','').strip()
        manager = request.POST.get('filter_manager','').strip()
        cycles_only = request.POST.get('filter_cycles') == 'on'
        sort_by = request.POST.get('sort_by','employee_id')
        try:
            sample_size = int(request.POST.get('sample_size') or 0)
        except ValueError:
            sample_size = 0

        # prepare display lists
        accepted = result.get('accepted', [])
        errors = result.get('errors', [])

        def matches(r):
            if dept and r['normalized'].get('department','') != dept:
                return False
            if manager and r.get('manager') != manager:
                return False
            if cycles_only and not r.get('in_cycle'):
                return False
            return True

        display_accepted = [r for r in accepted if matches(r)]
        display_errors = [r for r in errors if matches(r)]

        # sorting
        if sort_by == 'employee_name':
            display_accepted.sort(key=lambda r: r['normalized'].get('employee_name',''))
        elif sort_by == 'email':
            display_accepted.sort(key=lambda r: r['normalized'].get('email',''))
        else:
            display_accepted.sort(key=lambda r: r['normalized'].get('employee_id',''))

        if sample_size > 0:
            display_accepted = display_accepted[:sample_size]

        result['display_accepted'] = display_accepted
        result['display_errors'] = display_errors

        return render(request, 'upload.html', {'result': result, 'filters': {'department': dept, 'manager': manager, 'cycles_only': cycles_only, 'sort_by': sort_by, 'sample_size': sample_size}})
    return render(request, 'upload.html')


def download_errors_view(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('POST with file required')
    f = request.FILES.get('file')
    if not f:
        return HttpResponseBadRequest('No file uploaded')
    try:
        result = parse_csv(f.file)
    except ParseError as e:
        return HttpResponseBadRequest(str(e))

    # Prepare CSV of errors
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hris_errors.csv"'
    writer = csv.writer(response)
    writer.writerow(['source_row','employee_id','employee_name','errors','error_codes'])
    for r in result['errors']:
        writer.writerow([r['source_row'], r['normalized'].get('employee_id',''), r['normalized'].get('employee_name',''), '; '.join(r['errors']), ';'.join(r.get('error_codes',[]))])
    return response
