from django.core.mail import send_mail


FROM_ADDRESS = 'etd@brown.edu'
ACCEPT_MSG_TEMPLATE = u'''Dear {first_name} {last_name},\n\n
The manuscript of your dissertation, "{title}", satisfies all of the Graduate School's formatting requirements. \n\n
If you have not already done so, please submit all required paperwork to fulfill your completion requirements. As this paperwork is received, you will be notified (via the email address stored in your profile on the ETD system) and the Graduate School will update the checklist that appears on to the ETD website (http://library.brown.edu/etd).\n\n
Sincerely,\n
The Brown University Graduate School'''
REJECT_MSG_TEMPLATE = u'''"Dear {first_name} {last_name},\n\n
Your dissertation, "{title}", needs revision before it can be accepted by the Graduate School. The details of these required revisions are below:\n\n
{issues}\n\n
Please resubmit your dissertation once you have addressed the issues above. If you have any questions about these issues, please contact the Graduate School at Graduate_School@brown.edu or 401-863-2843.\n\n
Sincerely,\n
The Brown University Graduate School'''


def _accept_params(candidate):
    params = {}
    params['subject'] = u'Dissertation Submission Approved'
    params['message'] = ACCEPT_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            title=candidate.thesis.title)
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def _get_formatting_issues_msg(candidate):
    format_checklist = candidate.thesis.format_checklist
    issues_msg = u''
    if format_checklist.general_comments:
        issues_msg += u'General Comments:\n%s\n\n' % format_checklist.general_comments
    issues_msg += u'These elements of your dissertation are not properly formatted:\n\n'
    if format_checklist.title_page_comment:
        issues_msg += u'Title page: %s\n\n' % format_checklist.title_page_comment
    if format_checklist.signature_page_comment:
        issues_msg += u'Signature page: %s\n\n' % format_checklist.signature_page_comment
    if format_checklist.font_comment:
        issues_msg += u'Font: %s\n\n' % format_checklist.font_comment
    if format_checklist.spacing_comment:
        issues_msg += u'Spacing: %s\n\n' % format_checklist.spacing_comment
    if format_checklist.margins_comment:
        issues_msg += u'Margins: %s\n\n' % format_checklist.margins_comment
    if format_checklist.pagination_comment:
        issues_msg += u'Pagination: %s\n\n' % format_checklist.pagination_comment
    if format_checklist.format_comment:
        issues_msg += u'Format: %s\n\n' % format_checklist.format_comment
    if format_checklist.graphs_comment:
        issues_msg += u'Graphs: %s\n\n' % format_checklist.graphs_comment
    if format_checklist.dating_comment:
        issues_msg += u'Dating: %s\n\n' % format_checklist.dating_comment
    return issues_msg


def _reject_params(candidate):
    params = {}
    params['subject'] = u'Dissertation Submission Rejected'
    params['message'] = REJECT_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            title=candidate.thesis.title,
                            issues=_get_formatting_issues_msg(candidate))
    return params


def send_accept_email(candidate):
    params = _accept_params(candidate)
    send_mail(params['subject'], params['message'], params['from_address'], params['to_address'], fail_silently=False)


def send_reject_email(candidate):
    params = _reject_params(candidate)
    send_mail(params['subject'], params['message'], params['from_address'], params['to_address'], fail_silently=False)
