# error-reporting-tool - view definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

# Create your views here.
from __future__ import division
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse, render
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from Post.models import BuildFailure
from parser import Parser
from getInfo import Info
from createStatistics import Statistics
import json
import datetime
import urllib
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy
from django.contrib.sites.models import RequestSite
from django.http import JsonResponse

#TODO remove unused imports

class results_mode():
    LATEST = 0
    AUTOBUILDER = 1
    SEARCH = 2

def sort_elems(elems, ordering_string, default_orderby):
    aux = ordering_string
    if ordering_string:
        column, order = aux.split(':')
    else:
        column, order = default_orderby.split(':')
    if order == '-':
        rev = True
    else:
        rev = False

    if column == "submitted_on":
        elems.sort(key=lambda r : r.BUILD.DATE, reverse=not rev)
        return elems
    else:
        elems.sort(key=lambda r : r.BUILD.DATE, reverse=True) # Secondary sorting criteria

    if column == "machine":
        elems.sort(key=lambda r : r.BUILD.MACHINE, reverse=rev)
    elif column == "branch":
        elems.sort(key=lambda r : r.BUILD.BRANCH, reverse=rev)
    elif column == "target":
        elems.sort(key=lambda r : r.BUILD.TARGET, reverse=rev)
    elif column == "distro":
        elems.sort(key=lambda r : r.BUILD.DISTRO, reverse=rev)
    elif column == "nativelsbstring":
        elems.sort(key=lambda r : r.BUILD.NATIVELSBSTRING, reverse=rev)
    elif column == "build_sys":
        elems.sort(key=lambda r : r.BUILD.BUILD_SYS, reverse=rev)
    elif column == "target_sys":
        elems.sort(key=lambda r : r.BUILD.TARGET_SYS, reverse=rev)
    elif column == "submitter":
        elems.sort(key=lambda r : r.BUILD.NAME, reverse=rev)
    elif column == "email":
        elems.sort(key=lambda r : r.BUILD.EMAIL, reverse=rev)
    elif column == "task":
        elems.sort(key=lambda r : r.TASK, reverse=rev)
    elif column == "recipe":
        elems.sort(key=lambda r : r.RECIPE, reverse=rev)
    return elems

def _get_toggle_order(request, orderkey, reverse = False):
    if reverse:
        return "%s:+" % orderkey if request.GET.get('orderby', "") == "%s:-" % orderkey else "%s:-" % orderkey
    else:
        return "%s:-" % orderkey if request.GET.get('orderby', "") == "%s:+" % orderkey else "%s:+" % orderkey

def _get_toggle_order_icon(request, orderkey):
    if request.GET.get('orderby', "") == "%s:+"%orderkey:
        return "down"
    elif request.GET.get('orderby', "") == "%s:-"%orderkey:
        return "up"
    else:
        return ""

@csrf_exempt
def addData(request):
    response = ''
    current_id = -1
    if request.POST['data']:
        data = request.POST['data']
        p = Parser(data)
        current_id = p.parse()
        if current_id == -1:
           response = HttpResponse("The size of the file is too big.")
        else:
            response = reverse_lazy('your_entry', args=( 1, current_id))
            response = ''.join(['http://' ,RequestSite(request).domain, str(response)])
    return HttpResponse("Your entry can be found here: " +response)

@csrf_exempt
def returnUrl(request, page, query):
    return HttpResponse(request.get_full_path())

    return response

def apply_filter(context, items, name, value):
    # Look up the field name for filtering
    # e.g. filter_pair = (RECIPE, value)
    for col in context['tablecols']:
      if col['clclass'] == name:
        filter_pair = (col['field'], value)

    items = items.filter(filter_pair)
    return items

def search(request, mode=results_mode.LATEST):
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
        order_by = '-id'

    context = {
        'tablecols' : [
        {'name': 'Submitted on',
         'clclass' : 'submitted_on',
         'field' : 'BUILD__DATE',
        },
        {'name': 'Recipe',
         'clclass' : 'recipe',
         'field' : 'RECIPE',
        },
        {'name': 'Recipe version',
         'clclass': 'recipe_version',
         'field' : 'RECIPE_VERSION',
        },
        {'name': 'Task',
         'clclass': 'task',
         'field' : 'TASK',
        },
        {'name': 'Machine',
         'clclass': 'machine',
         'field': 'BUILD__MACHINE',
        },
        {'name': 'Distro',
         'clclass': 'distro',
         'field': 'BUILD__DISTRO',
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

    if mode == results_mode.AUTOBUILDER:
        # Temp until we have a better way to identify
        # autobuilder reports
        items = items.filter(BUILD__NAME__istartswith="yocto")
    elif mode == results_mode.SEARCH and request.GET.has_key("query"):
        items = items.filter(ERROR_DETAILS__icontains=request.GET['query'])


    # Do some special filtering to reduce the QuerySet to a manageable size
    # reversing or ordering the whole queryset is very expensive so we use
    # a range instead and then feed that to the paginator.
    if mode == results_mode.LATEST and not request.GET.has_key('filter'):
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
    results=''
    status_code = get_object_or_404(BuildFailure, pk=fail_id)
    build_failure = Info().getBFDetails(status_code.id)
    #TODO Fix this not needed?
    items = ""
    query = ""
    page = ""

    context = {'details' : build_failure,
               'page' : page,
               'query' : query,
               'items' : items
              }

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
