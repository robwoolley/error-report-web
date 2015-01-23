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
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from Post.models import BuildFailure
from parser import Parser
from django.conf import settings
from createStatistics import Statistics
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
import json
import urllib

class results_mode():
    LATEST = 0
    SPECIAL_SUBMITTER = 1
    SEARCH = 2
    BUILD = 3

# Any items here are added to the context for all pages
def common_context(request):
    ret = {}
    if hasattr(settings, "SPECIAL_SUBMITTER"):
        ret['special_submitter'] = settings.SPECIAL_SUBMITTER

    return ret


@csrf_exempt
def addData(request, return_json=False):
    response = ''
    if request.method == 'POST':
        # Backward compatibility with current send-error-report
        # The data is now in the request body in new django as it's
        # understandingand the data is application/json.
        # The json is url encoded so we need to undo this here.
        # [YOCTO #7245]

        data = request.body[len('data='):]
        data = urllib.unquote_plus(data)

        p = Parser(data)
        result = p.parse(request.META['HTTP_HOST'])

        if return_json:
          response = JsonResponse(result)
        else:
          response = HttpResponse("Your entry can be found here: "+result['build_url'])
    else:
        if return_json:
          response = JsonResponse({ 'error' : 'No valid data provided' })
        else:
          response = HttpResponse("No valid data provided")

    return response

def apply_filter(context, items, name, value):
    # Look up the field name for filtering
    # e.g. filter_pair = (RECIPE, value)
    for col in context['tablecols']:
      if col['clclass'] == name:
        filter_pair = (col['field'], value)

    items = items.filter(filter_pair)
    return items

def default(request):
    if hasattr(settings, "SPECIAL_SUBMITTER"):
        return redirect(search, mode=results_mode.SPECIAL_SUBMITTER)
    else:
        return redirect(search, mode=results_mode.LATEST)

def search(request, mode=results_mode.LATEST, build_id=None):
    # Default page limit
    limit = 25

    items = BuildFailure.objects.all()

    if request.GET.has_key("limit"):
        request.session['limit'] = request.GET['limit']

    if request.session.has_key('limit'):
        limit = request.session['limit']

    if request.GET.has_key("order_by"):
        order_by = request.GET['order_by']
    else:
        order_by = '-BUILD__DATE'

    context = {
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
        }],
    }


    if request.GET.has_key("filter"):
        items = apply_filter(context, items, request.GET['type'], request.GET['filter'])

    if mode == results_mode.SPECIAL_SUBMITTER and hasattr(settings,"SPECIAL_SUBMITTER"):
        #Special submitter mode see settings.py to enable
        name = settings.SPECIAL_SUBMITTER['name']
        items = items.filter(BUILD__NAME__istartswith=name)

    elif mode == results_mode.SEARCH and request.GET.has_key("query"):
        items = items.filter(ERROR_DETAILS__icontains=request.GET['query'])

    elif mode == results_mode.BUILD and build_id:
        items = items.filter(BUILD=build_id)

    # Do some special filtering to reduce the QuerySet to a manageable size
    # reversing or ordering the whole queryset is very expensive so we use
    # a range instead and then feed that to the paginator.
    elif mode == results_mode.LATEST and not request.GET.has_key('filter'):
        total = items.count()
        total_from = total - int(limit)
        if request.GET.has_key('page'):
          # fetch a 2 extra pages around the current page
          total_from = total - int(limit)*(int(request.GET['page'])+2)

        items = items.filter(id__range=(total_from,total))

    # Make sure we get django to do an inner join on our foreign key rather
    # than a query for each item
    items = items.select_related("BUILD").order_by(order_by)

    build_failures = Paginator(items, limit)

    if request.GET.has_key('page'):
        try:
            build_failures = build_failures.page(request.GET['page'])
        except EmptyPage:
            build_failures = build_failures.page(build_failures.num_pages)
    else:
        build_failures = build_failures.page(1)


    context['build_failures'] = build_failures


    return render(request, "latest-errors.html", context)


def details(request, template_name, fail_id):

    build_failure = BuildFailure.objects.filter(id=fail_id)
    build_failure = build_failure.select_related("BUILD")

    context = {'details' : build_failure }

    return render(request, template_name, context)

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

    return render_to_response("discretebarchart.html",
                              context,
                              RequestContext(request))
