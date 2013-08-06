from django.conf import settings
import mailsnake

def add_email_to_mailchimp_list(email_address, list_id, **kwargs):
    if not settings.MAILCHIMP_API_KEY:
        print "did not defined api key for Mailchimp, skip Mailchimp related action now"
        return False

    ms = mailsnake.MailSnake(settings.MAILCHIMP_API_KEY)
    ms.listSubscribe(
            id = list_id,
            email_address = email_address,
            update_existing = True,
            double_optin = False)

    return True

