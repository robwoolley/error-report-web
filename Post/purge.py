from datetime import datetime
from django.utils import timezone
import os
import sys

def setup_django():
    import django
    # Get access to our Django model
    newpath = os.path.abspath(os.path.dirname(__file__)) + '/..'
    sys.path.append(newpath)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
    django.setup()

def main():
    setup_django()
    from Post.models import BuildFailure
    items = BuildFailure.objects.all()
    now = timezone.now()
    for item in items:
        if item.REFERER == 'OTHER' or item.REFERER == 'NO_REFERER':
            continue
        difference = now - item.BUILD.DATE
        if difference.days > 30:
            item.delete()

if __name__ == "__main__":
    main()


