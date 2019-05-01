import logging
import os
import urllib
import requests
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseForbidden, JsonResponse, FileResponse, HttpResponseServerError
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Person, Candidate, Keyword, CommitteeMember
from .widgets import ID_VAL_SEPARATOR


BDR_EMAIL = 'bdr@brown.edu'
logger = logging.getLogger('etd')


def login(request):
    if request.user.is_authenticated():
        next_url = request.GET.get('next', reverse('home'))
        return HttpResponseRedirect(next_url)
    else:
        logger.error('login() - got anonymous user: %s' % request.META)
        return HttpResponseServerError('Internet Server error. Please contact %s for assistance.' % BDR_EMAIL)


def redirect_to_home(request):
    return HttpResponsePermanentRedirect(reverse('home'))


def home(request):
    return render(request, 'etd_app/home.html')


def overview(request):
    return render(request, 'etd_app/overview.html')


def faq(request):
    return render(request, 'etd_app/faq.html')


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


def get_shib_info_from_request(request):
    info = {}
    info['last_name'] = request.META.get('Shibboleth-sn', '')
    info['first_name'] = request.META.get('Shibboleth-givenName', '')
    info['email'] = request.META.get('Shibboleth-mail', '')
    return info


def _get_candidate(candidate_id, request):
    candidate = Candidate.objects.get(id=candidate_id)
    if candidate.person.netid != request.user.username:
        raise PermissionDenied
    return candidate


@login_required
def register(request):
    from .forms import PersonForm, CandidateForm
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['netid'] = request.user.username
        person_form = PersonForm(post_data, instance=get_person_instance(request))
        candidate_form = CandidateForm(post_data)
        if person_form.is_valid() and candidate_form.is_valid():
            person = person_form.save()
            banner_id = request.META.get('Shibboleth-brownBannerID', '')
            if banner_id:
                person.bannerid = banner_id
                person.save()
            candidate = candidate_form.save(commit=False)
            candidate.person = person
            candidate.save()
            return HttpResponseRedirect(reverse('candidate_home', kwargs={'candidate_id': candidate.id}))
    else:
        shib_info = get_shib_info_from_request(request)
        person_instance = get_person_instance(request)
        degree_type = request.GET.get('type', '')
        if person_instance:
            person_form = PersonForm(instance=person_instance, degree_type=degree_type)
        else:
            person_form = PersonForm(initial=shib_info, degree_type=degree_type)
        candidate_form = CandidateForm(degree_type=degree_type)
    return render(request, 'etd_app/register.html', {'person_form': person_form, 'candidate_form': candidate_form, 'register': True})


@login_required
def candidate_profile(request, candidate_id):
    from .forms import PersonForm, CandidateForm
    try:
        candidate = _get_candidate(candidate_id=candidate_id, request=request)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    if candidate.thesis.is_locked():
        return HttpResponseForbidden('Thesis has already been submitted and is locked.')
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['netid'] = request.user.username
        person_form = PersonForm(post_data, instance=candidate.person)
        candidate_form = CandidateForm(post_data, instance=candidate)
        if person_form.is_valid() and candidate_form.is_valid():
            person = person_form.save()
            banner_id = request.META.get('Shibboleth-brownBannerID', '')
            if banner_id:
                person.bannerid = banner_id
                person.save()
            candidate = candidate_form.save(commit=False)
            candidate.person = person
            candidate.save()
            return HttpResponseRedirect(reverse('candidate_home', kwargs={'candidate_id': candidate.id}))
    else:
        shib_info = get_shib_info_from_request(request)
        degree_type = request.GET.get('type', '')
        person_form = PersonForm(instance=candidate.person, degree_type=degree_type)
        candidate_form = CandidateForm(instance=candidate, degree_type=degree_type)
    return render(request, 'etd_app/register.html', {'person_form': person_form, 'candidate_form': candidate_form})


@login_required
def candidate_home(request, candidate_id=None):
    try:
        if candidate_id:
            candidate = _get_candidate(candidate_id=candidate_id, request=request)
        else:
            candidate = Candidate.objects.get(person__netid=request.user.username)
    except Candidate.DoesNotExist:
        type_ = request.GET.get('type', '')
        if type_:
            url = '%s?type=%s' % (reverse('register'), type_)
        else:
            url = reverse('register')
        return HttpResponseRedirect(url)
    except Candidate.MultipleObjectsReturned:
        candidate = Candidate.objects.filter(person__netid=request.user.username)[0]
    context_data = {'candidate': candidate}
    other_candidacies = Candidate.objects.filter(person__netid=request.user.username).exclude(id=candidate.id)
    if other_candidacies:
        context_data['other_candidacies'] = other_candidacies
    return render(request, 'etd_app/candidate.html', context_data)


@login_required
def candidate_upload(request, candidate_id):
    from .forms import UploadForm
    try:
        candidate = _get_candidate(candidate_id=candidate_id, request=request)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    if candidate.thesis.is_locked():
        return HttpResponseForbidden('Thesis has already been submitted and is locked.')
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save_upload(candidate)
            return HttpResponseRedirect(reverse('candidate_home', kwargs={'candidate_id': candidate.id}))
    else:
        form = UploadForm()
    return render(request, 'etd_app/candidate_upload.html', {'candidate': candidate, 'form': form})


def _user_keywords_changed(thesis, user_request_keywords):
    db_keywords_info = {}
    for kw in thesis.keywords.all():
        db_keywords_info[str(kw.id)] = kw
    unsorted_user_keywords = []
    for kw in user_request_keywords:
        if kw in db_keywords_info:
            unsorted_user_keywords.append(db_keywords_info[kw].text)
        else:
            unsorted_user_keywords.append(kw)
    db_keywords = sorted([kw.text for kw in db_keywords_info.values()])
    user_keywords = sorted([kw.split(ID_VAL_SEPARATOR)[-1] for kw in unsorted_user_keywords])
    if user_keywords and (user_keywords != db_keywords):
        return True
    return False


@login_required
def candidate_metadata(request, candidate_id):
    from .forms import MetadataForm
    try:
        candidate = _get_candidate(candidate_id=candidate_id, request=request)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    if candidate.thesis.is_locked():
        return HttpResponseForbidden('Thesis has already been submitted and is locked.')
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['candidate'] = candidate.id
        form = MetadataForm(post_data, instance=candidate.thesis)
        if form.is_valid():
            thesis = form.save()
            if thesis.abstract != form.cleaned_data['abstract']:
                messages.info(request, 'Your abstract contained invisible characters that we\'ve removed. Please make sure your abstract is correct in the information section below.')
            if thesis.title != form.cleaned_data['title']:
                messages.info(request, 'Your title contained invisible characters that we\'ve removed. Please make sure your title is correct in the information section below.')
            if _user_keywords_changed(thesis, request.POST.getlist('keywords', [])):
                messages.info(request, 'Your keywords contained invisible characters that we\'ve removed. Please make sure your keywords are correct in the information section below.')
            return HttpResponseRedirect(reverse('candidate_home', kwargs={'candidate_id': candidate.id}))
    else:
        form = MetadataForm(instance=candidate.thesis)
    context = {'candidate': candidate, 'form': form, 'ID_VAL_SEPARATOR': ID_VAL_SEPARATOR}
    return render(request, 'etd_app/candidate_metadata.html', context)


@login_required
def candidate_committee(request, candidate_id):
    from .forms import CommitteeMemberPersonForm, CommitteeMemberForm
    try:
        candidate = _get_candidate(candidate_id=candidate_id, request=request)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    if candidate.thesis.is_locked():
        return HttpResponseForbidden('Thesis has already been submitted and is locked.')
    if request.method == 'POST':
        person_form = CommitteeMemberPersonForm(request.POST)
        committee_member_form = CommitteeMemberForm(request.POST)
        if person_form.is_valid() and committee_member_form.is_valid():
            person = person_form.save()
            committee_member = committee_member_form.save(commit=False)
            committee_member.person = person
            committee_member.save()
            candidate.committee_members.add(committee_member)
            return HttpResponseRedirect(reverse('candidate_home', kwargs={'candidate_id': candidate.id}))
    else:
        person_form = CommitteeMemberPersonForm()
        committee_member_form = CommitteeMemberForm()
    context = {'candidate': candidate, 'person_form': person_form,
               'committee_member_form': committee_member_form}
    return render(request, 'etd_app/candidate_committee.html', context)


@login_required
@require_http_methods(['POST'])
def candidate_committee_remove(request, candidate_id, cm_id):
    try:
        candidate = _get_candidate(candidate_id=candidate_id, request=request)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    cm = CommitteeMember.objects.get(id=cm_id)
    candidate.committee_members.remove(cm)
    return HttpResponseRedirect(reverse('candidate_home', kwargs={'candidate_id': candidate.id}))


@login_required
def candidate_preview_submission(request, candidate_id):
    try:
        candidate = _get_candidate(candidate_id=candidate_id, request=request)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    return render(request, 'etd_app/candidate_preview.html', {'candidate': candidate})


@login_required
@require_http_methods(['POST'])
def candidate_submit(request, candidate_id):
    try:
        candidate = _get_candidate(candidate_id=candidate_id, request=request)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    candidate.thesis.submit()
    return HttpResponseRedirect(reverse('candidate_home', kwargs={'candidate_id': candidate.id}))


@login_required
@permission_required('etd_app.change_candidate', raise_exception=True)
def staff_home(request):
    return HttpResponseRedirect(reverse('review_candidates', kwargs={'status': 'all'}))


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
def view_abstract(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, 'etd_app/staff_view_abstract.html', {'candidate': candidate})


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


@login_required
def view_file(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    if candidate.person.netid != request.user.username:
        if not request.user.has_perm('etd_app.change_candidate'):
            return HttpResponseForbidden('You don\'t have permission to view this candidate\'s thesis.')
    if not candidate.thesis.current_file_name:
        return HttpResponse('Couldn\'t find a file: please email %s if there should be one.' % BDR_EMAIL)
    file_path = os.path.join(settings.MEDIA_ROOT, candidate.thesis.current_file_name)
    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % candidate.thesis.original_file_name
    return response


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
    url = '%s?query=%s&queryIndex=%s' % (settings.FAST_LOOKUP_BASE_URL, urllib.parse.quote(term), index)
    url = '%s&queryReturn=%s&suggest=autoSubject' % (url, urllib.parse.quote('idroot,auth,type,%s' % index))
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
        if select2_results:
            return [{'text': 'FAST results', 'children': select2_results}]
        else:
            return []
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
