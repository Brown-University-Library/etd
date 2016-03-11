from django.core.mail import send_mail
from django.utils import timezone


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
PAPERWORK_INFO = {
        'dissertation_fee': {'subject': u'Dissertation Fee', 'description': u'Cashier\'s Office receipt'},
        'bursar_receipt': {'subject': u'Bursar\'s Letter', 'description': u'Bursar\'s Office letter of clearance'},
        'gradschool_exit_survey': {'subject': u'Graduate Exit Survey', 'description': u'graduate exit survey'},
        'earned_docs_survey': {'subject': u'Survey of Earned Doctorates', 'description': u'Survey of Earned Doctorates'},
        'signature_pages': {'subject': u'Signature Pages', 'description': u'signature, abstract, and title pages'},
    }
PAPERWORK_MSG_TEMPLATE = u'''Dear {first_name} {last_name},\n\n
Your {description} were received by the Graduate School on {now}\n\n
Please submit any outstanding paperwork that is required to fulfill your completion requirements. As this paperwork is received, you will be notified (via the email address stored in your profile on the ETD system) and the Graduate School will update the checklist that appears on to the ETD website (http://library.brown.edu/etd).\n\n
Sincerely,\n
The Brown University Graduate School'''
COMPLETE_MSG_TEMPLATE = u'''Dear {first_name} {last_name},\n\n
Congratulations! Your dissertation, {title}, and all of the paperwork associated with your completion requirements have been received by the Graduate School. An official, written notification regarding the completion of your doctoral degree at Brown will be sent to you in the coming days (this email is automatically generated and, as such, is not an official communication).\n\n
For information about this year's Commencement exercises, please visit the University's Commencement website: http://www.brown.edu/commencement (the timeliness of the material on this site will depend on the date of your submission). If you have questions or concerns about your completion or the Commencement ceremony that are not addressed on the website, please send us email, Graduate_School@brown.edu.\n\n
Congratulations again on your accomplishment. All of Brown wishes you the best of luck and great success in your future.\n\n
Sincerely,\n
The Brown University Graduate School\n'''


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


def _reject_params(candidate):
    params = {}
    params['subject'] = u'Dissertation Submission Rejected'
    params['message'] = REJECT_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            title=candidate.thesis.title,
                            issues=_get_formatting_issues_msg(candidate))
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def _paperwork_params(candidate, item_completed):
    params = {}
    params['subject'] = PAPERWORK_INFO[item_completed]['subject']
    params['message'] = PAPERWORK_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            description=PAPERWORK_INFO[item_completed]['description'],
                            now=timezone.now())
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def _complete_params(candidate):
    params = {}
    params['subject'] = u'Submission Process Complete'
    params['message'] = COMPLETE_MSG_TEMPLATE.format(
                            first_name=candidate.person.first_name,
                            last_name=candidate.person.last_name,
                            title=candidate.thesis.title)
    params['to_address'] = [candidate.person.email]
    params['from_address'] = FROM_ADDRESS
    return params


def send_accept_email(candidate):
    params = _accept_params(candidate)
    send_mail(params['subject'], params['message'], params['from_address'], params['to_address'], fail_silently=False)


def send_reject_email(candidate):
    params = _reject_params(candidate)
    send_mail(params['subject'], params['message'], params['from_address'], params['to_address'], fail_silently=False)


def send_paperwork_email(candidate, item_completed):
    params = _paperwork_params(candidate, item_completed)
    send_mail(params['subject'], params['message'], params['from_address'], params['to_address'], fail_silently=False)


def send_complete_email(candidate):
    params = _complete_params(candidate)
    send_mail(params['subject'], params['message'], params['from_address'], params['to_address'], fail_silently=False)
