from django.utils.translation import ugettext as _

def post_init(sender, **kwargs):
    """Class is ready, all attributes has been set """
    instance = kwargs['instance']

    """Loop through translation fields and set the gettext in beetween """
    if hasattr(sender, '_translation_fields'):
        for x in sender._translation_fields:
            value = getattr(instance, x)
            setattr(instance, x, _(value))
