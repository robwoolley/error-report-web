from datetime import datetime, timedelta
from django.utils import timezone
import os
import sys

def setup_django():
    import django
    # Get access to our Django model
    newpath = os.path.abspath(os.path.dirname(__file__)) + '/..'
    sys.path.append(newpath)
    if not os.getenv('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'
    django.setup()

def main():
    setup_django()
    from Post.models import BuildFailure
    delete_before = timezone.now()-timedelta(days=30)
    query = "SELECT bf.id FROM Post_buildfailure bf LEFT JOIN Post_build b ON (bf.BUILD_id = b.id) WHERE bf.REFERER NOT IN ('OTHER','NO_REFERER') AND b.DATE < '{0}'".format(delete_before.date())
    print query
    items = BuildFailure.objects.raw(query)
    for item in items:
        item.delete()

if __name__ == "__main__":
    main()
