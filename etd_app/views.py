from __future__ import unicode_literals
import logging
import urllib
import requests
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseServerError
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Person, Candidate, Keyword, CommitteeMember
from .widgets import ID_VAL_SEPARATOR


logger = logging.getLogger('etd')


def login(request):
    if request.user.is_authenticated():
        next_url = request.GET.get('next', reverse('home'))
        return HttpResponseRedirect(next_url)
    else:
        logger.error('login() - got anonymous user: %s' % request.META)
        return HttpResponseServerError('Internet Server error. Please contact bdr@brown.edu for assistance.')


def home(request):
    return render(request, 'etd_app/home.html')


def overview(request):
    return render(request, 'etd_app/overview.html')


def faq(request):
    return render(request, 'etd_app/faq.html')


def tutorials(request):
    return render(request, 'etd_app/tutorials.html')


def copyright(request):
    return render(request, 'etd_app/copyright.html')


def get_person_instance(request):
    person_instance = None
    try:
        person_instance = Person.objects.get(netid=request.user.username)
    except Person.DoesNotExist:
        if 'orcid' in request.POST:
            try:
                person_instance = Person.objects.get(orcid=request.POST['orcid'])
            except Person.DoesNotExist:
                pass
    return person_instance


def get_candidate_instance(request):
    try:
        candidate_instance = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        candidate_instance = None
    return candidate_instance


def get_shib_info_from_request(request):
    info = {}
    info['last_name'] = request.META.get('Shibboleth-sn', '')
    info['first_name'] = request.META.get('Shibboleth-givenName', '')
    info['email'] = request.META.get('Shibboleth-mail', '')
    return info


@login_required
def register(request):
    from .forms import PersonForm, CandidateForm
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['netid'] = request.user.username
        person_form = PersonForm(post_data, instance=get_person_instance(request))
        candidate_form = CandidateForm(post_data, instance=get_candidate_instance(request))
        if person_form.is_valid() and candidate_form.is_valid():
            person = person_form.save()
            candidate = candidate_form.save(commit=False)
            candidate.person = person
            candidate.save()
            return HttpResponseRedirect(reverse('candidate_home'))
    else:
        shib_info = get_shib_info_from_request(request)
        person_instance = get_person_instance(request)
        if person_instance:
            person_form = PersonForm(instance=person_instance)
        else:
            person_form = PersonForm(initial=shib_info)
        candidate_form = CandidateForm(instance=get_candidate_instance(request))
    return render(request, 'etd_app/register.html', {'person_form': person_form, 'candidate_form': candidate_form})


@login_required
def candidate_home(request):
    try:
        candidate = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    context_data = {'candidate': candidate}
    return render(request, 'etd_app/candidate.html', context_data)


@login_required
def candidate_upload(request):
    from .forms import UploadForm
    try:
        candidate = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    if candidate.thesis.is_accepted():
        return HttpResponseForbidden('thesis has already been accepted')
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save_upload(candidate)
            return HttpResponseRedirect(reverse('candidate_home'))
    else:
        form = UploadForm()
    return render(request, 'etd_app/candidate_upload.html', {'candidate': candidate, 'form': form})


@login_required
def candidate_metadata(request):
    from .forms import MetadataForm
    try:
        candidate = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['candidate'] = candidate.id
        form = MetadataForm(post_data, instance=candidate.thesis)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('candidate_home'))
    else:
        form = MetadataForm(instance=candidate.thesis)
    context = {'candidate': candidate, 'form': form, 'ID_VAL_SEPARATOR': ID_VAL_SEPARATOR}
    return render(request, 'etd_app/candidate_metadata.html', context)


@login_required
def candidate_committee(request):
    from .forms import CommitteeMemberPersonForm, CommitteeMemberForm
    try:
        candidate = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    if request.method == 'POST':
        person_form = CommitteeMemberPersonForm(request.POST)
        committee_member_form = CommitteeMemberForm(request.POST)
        if person_form.is_valid() and committee_member_form.is_valid():
            person = person_form.save()
            committee_member = committee_member_form.save(commit=False)
            committee_member.person = person
            committee_member.save()
            candidate.committee_members.add(committee_member)
            return HttpResponseRedirect(reverse('candidate_home'))
    else:
        person_form = CommitteeMemberPersonForm()
        committee_member_form = CommitteeMemberForm()
    context = {'candidate': candidate, 'person_form': person_form,
               'committee_member_form': committee_member_form}
    return render(request, 'etd_app/candidate_committee.html', context)


@login_required
@require_http_methods(['POST'])
def candidate_committee_remove(request, cm_id):
    try:
        candidate = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    cm = CommitteeMember.objects.get(id=cm_id)
    candidate.committee_members.remove(cm)
    return HttpResponseRedirect(reverse('candidate_home'))


@login_required
@require_http_methods(['POST'])
def candidate_submit(request):
    try:
        candidate = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    candidate.thesis.submit()
    return HttpResponseRedirect(reverse('candidate_home'))


@login_required
@permission_required('etd_app.change_candidate', raise_exception=True)
def staff_home(request):
    return render(request, 'etd_app/staff_base.html')


@login_required
@permission_required('etd_app.change_candidate', raise_exception=True)
def staff_view_candidates(request, status):
    if 'sort_by' in request.GET:
        candidates = Candidate.get_candidates_by_status(status, sort_param=request.GET['sort_by'])
    else:
        candidates = Candidate.get_candidates_by_status(status)
    return render(request, 'etd_app/staff_view_candidates.html', {'candidates': candidates, 'status': status})


@login_required
@permission_required('etd_app.change_candidate', raise_exception=True)
def staff_approve(request, candidate_id):
    from .forms import GradschoolChecklistForm, FormatChecklistForm
    candidate = get_object_or_404(Candidate, id=candidate_id)
    if request.method == 'POST':
        form = GradschoolChecklistForm(request.POST)
        if form.is_valid():
            form.save_data(candidate)
            return HttpResponseRedirect(reverse('staff_home'))
    else:
        format_form = FormatChecklistForm(instance=candidate.thesis.format_checklist)
    context = {'candidate': candidate, 'format_form': format_form}
    return render(request, 'etd_app/staff_approve_candidate.html', context)


@login_required
@permission_required('etd_app.change_candidate', raise_exception=True)
@require_http_methods(['POST'])
def staff_format_post(request, candidate_id):
    from .forms import FormatChecklistForm
    candidate = get_object_or_404(Candidate, id=candidate_id)
    format_form = FormatChecklistForm(request.POST, instance=candidate.thesis.format_checklist)
    if format_form.is_valid():
        format_form.handle_post(request.POST, candidate)
        return HttpResponseRedirect(reverse('approve', kwargs={'candidate_id': candidate_id}))


def _select2_list(search_results):
    select2_results = []
    for r in search_results:
        select2_results.append({'id': r.id, 'text': r.text})
    return select2_results


def _get_previously_used(model, term):
    keywords = Keyword.search(term=term, order='text')
    if len(keywords) > 0:
        return [{'text': 'Previously Used', 'children': _select2_list(keywords)}]
    else:
        return []


def _build_fast_url(term, index):
    url = '%s?query=%s&queryIndex=%s' % (settings.FAST_LOOKUP_BASE_URL, urllib.quote(term.encode('utf8')), index)
    url = '%s&queryReturn=%s&suggest=autoSubject' % (url, urllib.quote('idroot,auth,type,%s' % index))
    return url


def _fast_results_to_select2_list(fast_results, index):
    results = []
    fast_ids = []
    for item in fast_results:
        text = item['auth']
        if item['type'] != 'auth':
            text = '%s (%s)' % (text, item[index][0])
        if item['idroot'] not in fast_ids:
            results.append({'id': '%s%s%s' % (item['idroot'], ID_VAL_SEPARATOR, item['auth']), 'text': text})
            fast_ids.append(item['idroot'])
    return results


def _get_fast_results(term, index='suggestall'):
    error_response = [{'text': 'FAST results', 'children': [{'id': '', 'text': 'Error retrieving FAST results.'}]}]
    url = _build_fast_url(term, index)
    try:
        r = requests.get(url, timeout=2)
    except requests.exceptions.Timeout:
        logger.error('fast lookup timed out')
        return error_response
    except Exception:
        import traceback
        logger.error('fast lookup exception: %s' % traceback.format_exc())
        return error_response
    try:
        select2_results = _fast_results_to_select2_list(r.json()['response']['docs'], index)
        return [{'text': 'FAST results', 'children': select2_results}]
    except Exception as e:
        logger.error('fast data exception: %s' % e)
        logger.error('fast response: %s - %s' % (r.status_code, r.text))
        return error_response


@login_required
def autocomplete_keywords(request):
    term = request.GET['term']
    results = _get_previously_used(Keyword, term)
    results.extend(_get_fast_results(term))
    return JsonResponse({'err': 'nil', 'results': results})
