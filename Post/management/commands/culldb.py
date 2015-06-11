# error-reporting-tool -  culldb
#
# Copyright (C) 2015 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

# Create your views here.
# vi: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from django.core.management.base import BaseCommand, CommandError
from Post.models import Build, BuildFailure
from optparse import make_option
import time
import sys

class Command(BaseCommand):
    help = 'Culls the database to size in rows'
    args = '<size>'
    option_list = BaseCommand.option_list + (
        make_option('-i',
                    '--info',
                    dest='info',
                    action="store_true",
                    help='Show the current database size'),
    )

    def handle(self, *args, **options):
        count = Build.objects.count()

        if options['info']:
            print "Current builds table size: %d" % Build.objects.count()
            return

        if len(args) > 0 and args[0]:
            try:
                new_size = int(args[0])
            except ValueError:
                print "Not a valid size"
                return


            num_to_delete = count - new_size
            print "\nReducing the database size to %d which will DELETE %d rows" % (new_size, num_to_delete)
            i = 1
            while i != 0:
                i = i-1
                print 'Ctrl+c TO CANCEL. Executing in... %d \r' % i,
                sys.stdout.flush()
                time.sleep(1)

            q = Build.objects.all()[:num_to_delete].values_list('pk',
                                                                flat=True)
            Build.objects.filter(pk__in=list(q)).delete()
