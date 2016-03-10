import logging
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Person, Candidate, Thesis, Keyword


logger = logging.getLogger('etd')


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


@login_required
def register(request):
    from .forms import PersonForm, CandidateForm
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data[u'netid'] = request.user.username
        person_form = PersonForm(post_data, instance=get_person_instance(request))
        candidate_form = CandidateForm(post_data, instance=get_candidate_instance(request))
        if person_form.is_valid() and candidate_form.is_valid():
            person = person_form.save()
            candidate = candidate_form.save(commit=False)
            candidate.person = person
            candidate.save()
            return HttpResponseRedirect(reverse('candidate_home'))
    else:
        person_form = PersonForm(instance=get_person_instance(request))
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
            form.save_metadata(candidate)
            return HttpResponseRedirect(reverse('candidate_home'))
    else:
        form = MetadataForm(instance=candidate.thesis)
    return render(request, 'etd_app/candidate_metadata.html', {'candidate': candidate, 'form': form})


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


def select2_list(queryset):
    results = []
    for r in queryset.order_by('text'):
        results.append({'id': r.id, 'text': r.text})
    return results


def get_keyword_results(request):
    term = request.GET['term']
    #this is search, so we're fine with getting fuzzy results
    #  so search the lower-case, no-accent version as well
    queryset = Keyword.objects.filter(Q(text__icontains=term) | Q(search_text__icontains=term))
    results = select2_list(queryset)
    return results


@login_required
def autocomplete_keywords(request):
    return JsonResponse({'err': 'nil', 'results': get_keyword_results(request)})
