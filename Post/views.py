# error-reporting-tool - view definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

# Create your views here.
# vi: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import division
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from Post.models import BuildFailure
from parser import Parser
from django.conf import settings
from createStatistics import Statistics
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.http import JsonResponse
from django.db.models import Q
import json
import urllib

class results_mode(object):
    LATEST = 0
    SPECIAL_SUBMITTER = 1
    SEARCH = 2
    BUILD = 3
    SIMILAR_TO = 4

# Any items here are added to the context for all pages
def common_context(request):
    #Make the initial mode state -1 to indicate unset for use in the base template
    ret = {
        'mode' : -1,
    }

    if hasattr(settings, "SPECIAL_SUBMITTER"):
        ret['special_submitter'] = settings.SPECIAL_SUBMITTER

    return ret


@csrf_exempt
def addData(request, return_json=False):
    response = ''
    if request.method == 'POST':
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        if "send-error-report/0.3" in user_agent:
            data = request.body
        else:
            # Backward compatibility with send-error-report < 0.3
            # The json is url encoded so we need to undo this here.
            data = request.body[len('data='):]
            data = urllib.unquote_plus(data)

        p = Parser(data)
        result = p.parse(request)

        if return_json:
            response = JsonResponse(result)
        else:
            if not result.has_key('error'):
              response = HttpResponse("Your entry can be found here: "+result['build_url'])
            else:
              response = HttpResponse(result['error'])

        if result.has_key('error'):
            response.status_code=500
    else:
        if return_json:
            response = JsonResponse({ 'error' : 'No valid data provided',
                                      'max_log_size' : settings.MAX_UPLOAD_SIZE,
                                    })
        else:
            response = HttpResponse("No valid data provided", status=200)

    return response

def apply_filter(context, items, name, value):
    # Look up the field name for filtering
    # e.g. filter_pair = (RECIPE, value)
    filter_pair = None

    for col in context['tablecols']:
      if col['clclass'] == name:
        filter_pair = (col['field'], value)

    if not filter_pair:
        return items

    items = items.filter(filter_pair)
    return items

def default(request):
    if hasattr(settings, "SPECIAL_SUBMITTER"):
        return redirect(search, mode=results_mode.SPECIAL_SUBMITTER)
    else:
        return redirect(search, mode=results_mode.LATEST)

def search(request, mode=results_mode.LATEST, **kwargs):
    # Default page limit
    limit = 25

    items = BuildFailure.objects.all()

    if request.GET.has_key("limit"):
        try:
            n_limit = int(request.GET['limit'])
            if n_limit > 0:
                limit = n_limit
        except ValueError:
            # just use the Default page limit
            pass

    request.session['limit'] = limit

    # Default page = 1
    page = request.GET.get('page', 1)

    # Default order_by -BUILD__DATE
    order_by = request.GET.get("order_by", '-BUILD__DATE')

    context = {
        'results_mode' : results_mode,
        'mode' : mode,
        'args' : kwargs,
        'tablecols' : [
        {'name': 'Submitted on',
         'clclass' : 'submitted_on',
         'field' : 'BUILD__DATE',
         'disable_toggle' : True,
        },
        {'name': 'Recipe',
         'clclass' : 'recipe',
         'field' : 'RECIPE',
         'disable_toggle' : True,
        },
        {'name': 'Recipe version',
         'clclass': 'recipe_version',
         'field' : 'RECIPE_VERSION',
        },
        {'name': 'Task',
         'clclass': 'task',
         'field' : 'TASK',
         'disable_toggle' : True,
        },
        {'name': 'Machine',
         'clclass': 'machine',
         'field': 'BUILD__MACHINE',
         'disable_toggle' : True,
        },
        {'name': 'Distro',
         'clclass': 'distro',
         'field': 'BUILD__DISTRO',
         'disable_toggle' : True,
        },
        {'name': 'Build system',
         'clclass': 'build_sys',
         'field': 'BUILD__BUILD_SYS',
        },
        {'name': 'Target system',
         'clclass': 'target_sys',
         'field': 'BUILD__TARGET_SYS',
        },
        {'name': 'Host distro',
         'clclass': 'nativelsbstring',
         'field': 'BUILD__NATIVELSBSTRING',
        },
        {'name': 'Branch',
         'clclass': 'branch',
         'field': 'BUILD__BRANCH',
        },
        {'name': 'Commit',
         'clclass': 'commit',
         'field': 'BUILD__COMMIT',
        },
        {'name': 'Submitter',
         'clclass': 'submitter',
         'field': 'BUILD__NAME',
        },
        {'name': 'Similar',
         'clclass': 'similar',
        }
      ],
    }

    if request.GET.has_key("filter") and request.GET.has_key("type"):
        items = apply_filter(context, items, request.GET['type'], request.GET['filter'])

    if mode == results_mode.SPECIAL_SUBMITTER and hasattr(settings,"SPECIAL_SUBMITTER"):
        #Special submitter mode see settings.py to enable
        name = settings.SPECIAL_SUBMITTER['name']
        items = items.filter(BUILD__NAME__istartswith=name)

    elif mode == results_mode.SEARCH and request.GET.has_key("query"):
        query = request.GET["query"]

        items = items.filter(
                             Q(BUILD__NAME__icontains=query) |
                             Q(BUILD__DISTRO__icontains=query) |
                             Q(BUILD__MACHINE__icontains=query) |
                             Q(RECIPE__icontains=query) |
                             Q(BUILD__NATIVELSBSTRING__icontains=query) |
                             Q(BUILD__COMMIT__icontains=query) |
                             Q(BUILD__BRANCH__icontains=query) |
                             Q(TASK__icontains=query) |
                             Q(ERROR_DETAILS__icontains=query))

    elif mode == results_mode.BUILD and 'build_id' in kwargs:
        items = items.filter(BUILD=kwargs['build_id'])
    elif mode == results_mode.SIMILAR_TO and 'fail_id' in kwargs:
        try:
            items = BuildFailure.objects.get(id=kwargs['fail_id']).get_similar_fails()
        except ObjectDoesNotExist:
            # Sabotage the queryset to 0 items so that we fail gracefully to
            # "no results found"
            items = items.filter(id=-1)

    # Do some special filtering to reduce the QuerySet to a manageable size
    # reversing or ordering the whole queryset is very expensive so we use
    # a range instead and then feed that to the paginator.
    elif mode == results_mode.LATEST and not request.GET.has_key('filter'):
        total = items.count()
        # Get an extra two pages worth to populate the paginator
        try:
            total_from = total - limit*(int(page)+2)
        except:
            total_from = total - limit

        items = items.filter(id__range=(total_from,total))

    # Make sure we get django to do an inner join on our foreign key rather
    # than a query for each item
    items = items.select_related("BUILD").order_by(order_by)

    build_failures = Paginator(items, limit)

    try:
        build_failures = build_failures.page(page)
    except:
        build_failures = build_failures.page(build_failures.num_pages)

    context['build_failures'] = build_failures

    # We don't know if the order_by will be valid right up until the sql
    # query is executed during render so we have to catch an invalid order_by
    # here
    try:
        return render(request, "latest-errors.html", context)
    except FieldError:
        items = items.order_by()
        return render(request, "latest-errors.html", context)


def details(request, fail_id):
    try:
      build_failure = BuildFailure.objects.get(id=fail_id)
    except ObjectDoesNotExist:
      build_failure = None

    context = {'detail' : build_failure }

    return render(request, "error-details.html", context)

@csrf_exempt
def chart(request, template_name, key):
    data=""
    s = Statistics()
    alldata = s.chart_statistics(key)
    if (alldata == {}):
        return HttpResponse("")

    data = json.dumps([{ 'values': list(alldata)}])
    # Replace MACHINE with x and dcount with value
    # We do this in the string as it's more efficient
    data = data.replace(key, "x")
    data = data.replace("dcount", "y")

    context = { 'data' : data,
               'chart_id': key,
              }

    return render(request,
                  "discretebarchart.html",
                  context)
