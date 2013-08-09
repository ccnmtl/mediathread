from django.conf import settings
import mailsnake


def add_email_to_mailchimp_list(email_address, list_id, **kwargs):
    merge_vars_dict = {}
    if kwargs.has_key('fname'):
        merge_vars_dict['FNAME'] = kwargs['fname']
    if kwargs.has_key('lname'):
        merge_vars_dict['LNAME'] = kwargs['lname']

    if not settings.MAILCHIMP_API_KEY:
        print "did not defined api key for Mailchimp, skip Mailchimp related action now"
        return False

    ms = mailsnake.MailSnake(settings.MAILCHIMP_API_KEY)
    ms.listSubscribe(
        id=list_id,
        email_address=email_address,
        merge_vars=merge_vars_dict,
        update_existing=True,
        double_optin=False)

    return True


def display_user(user):
    if user.first_name or user.last_name:
        return user.get_full_name()
    else:
        return user.username
