from django import template


register = template.Library()


@register.filter
def int_to_term(n):
    """Convert a numerical semester into a string."""
    try:
        n = int(n)
    except ValueError:
        return None

    if n > 0 and n < 4:
        return ['Spring', 'Summer', 'Fall'][n - 1]
    else:
        return None
