# error-reporting-tool - view definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

# Create your views here.
from __future__ import division
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.shortcuts import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from Post.models import Build, BuildFailure
from django.contrib.auth import authenticate
from django.core.mail import send_mail, BadHeaderError
import os, sys, random
from parser import Parser
from getInfo import Info
from createStatistics import Statistics
from django.utils import simplejson
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.sites.models import RequestSite
from collections import OrderedDict

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

def viewEntry(request,template_name, page=None, query=None):
    return HttpResponseRedirect(reverse('entry', args=(), kwargs={"items":10, "page":page, "query":query}))

@csrf_exempt
def search(request, template_name, items = None, page = None, query = None, orderby = None, filter = None):
    if items == None and page == None and query == None:
         page = request.GET.get('page', '')
         query = request.GET.get('query', '')
         items = request.GET.get('items', '')
         orderby = request.GET.get('orderby', '')
         filter_string = request.GET.get('filter', '')

    default_orderby = 'submitted_on:+';

    # can't filter and order by the same column
    if orderby:
        orderby_column, order = orderby.split(':')
        if filter_string and orderby_column.upper() in filter_string:
            orderby = ""

    if orderby == "":
        get_values = request.GET.copy()
        get_values['orderby'] = default_orderby
        request.GET = get_values

    latest = False
    if "latest" in query:
         latest = True
         query = query.replace("_latest", "")

    if query == "" or query.isspace():
        query = "all"
    (elems, non_filtered_elems) = Info().getSearchResult(query.strip(), filter_string)
    elems = sort_elems(elems, orderby, default_orderby)
    no = len(elems)
    if no == 0:
        return render_to_response("error-page.html", {"latest" : latest,  "query" : query}, RequestContext(request))

    if latest is True:
        if no > 150:
            elems = elems[:150]
            no = 150

    paginator = Paginator(elems, items)
    try:
        c = paginator.page(page)
    except PageNotAnInteger:
        c = paginator.page(1)
    except EmptyPage:
        c=paginator.page(paginator.num_pages)

    if c.number <= 3:
        index = 0
        end = 5
    elif paginator.num_pages - paginator.page_range.index(c.number) <= 2:
        diff = paginator.num_pages - paginator.page_range.index(c.number)
        index = paginator.page_range.index(c.number) - 5 + diff
        if index < 0:
            index = 0
        end = paginator.page_range.index(c.number) + diff
    else:
        index = paginator.page_range.index(c.number) - 2
        end = index + 5

    context = {
        'details':c,
        'non_filtered_details' : non_filtered_elems,
        'd' : query,
        "no" : no,
        'list' : paginator.page_range[index:end],
        'items' : items,
        'orderby': orderby,
        'default_orderby' : default_orderby,
        'filter_string' : filter_string,
        'objectname' : 'errors',
        'tablecols' : [
        {'name': 'Submitted on',
         'orderfield': _get_toggle_order(request, "submitted_on", True),      # adds ordering by the field value;
         'ordericon':_get_toggle_order_icon(request, "submitted_on"),
        },
        {'name': 'Recipe',
         'filter': 'RECIPE',
         'orderfield': _get_toggle_order(request, "recipe", False),
         'ordericon':_get_toggle_order_icon(request, "recipe"),
        },
        {'name': 'Recipe version',
         'clclass': 'recipe_version',
        },
        {'name': 'Task',
         'filter': 'TASK',
         'orderfield': _get_toggle_order(request, "task", False),
         'ordericon':_get_toggle_order_icon(request, "task"),
        },
        {'name': 'Machine',
         'filter': 'MACHINE',
         'orderfield': _get_toggle_order(request, "machine", False),
         'ordericon':_get_toggle_order_icon(request, "machine"),
        },
        {'name': 'Distro',
         'filter': 'DISTRO',
         'orderfield': _get_toggle_order(request, "distro", False),
         'ordericon':_get_toggle_order_icon(request, "distro"),
        },
        {'name': 'Build system',
         'filter': 'BUILD_SYS',
         'clclass': 'build_sys',
         'hidden': 1,
         'orderfield': _get_toggle_order(request, "build_sys", False),
         'ordericon':_get_toggle_order_icon(request, "build_sys"),
        },
        {'name': 'Target system',
         'filter': 'TARGET_SYS',
         'clclass': 'target_sys',
         'hidden': 1,
         'orderfield': _get_toggle_order(request, "target_sys", False),
         'ordericon':_get_toggle_order_icon(request, "target_sys"),
        },
        {'name': 'Host distro',
         'filter': 'NATIVELSBSTRING',
         'clclass': 'nativelsbstring',
         'orderfield': _get_toggle_order(request, "nativelsbstring", False),
         'ordericon':_get_toggle_order_icon(request, "nativelsbstring"),
        },
        {'name': 'Branch',
         'filter': 'BRANCH',
         'clclass': 'branch',
         'orderfield': _get_toggle_order(request, "branch", False),
         'ordericon':_get_toggle_order_icon(request, "branch"),
        },
        {'name': 'Commit',
         'filter': 'COMMIT',
         'clclass': 'commit',
        },
        {'name': 'Submitter',
         'filter': 'NAME',
         'clclass': 'submitter',
         'hidden': 1,
         'orderfield': _get_toggle_order(request, "submitter", False),
         'ordericon':_get_toggle_order_icon(request, "submitter"),
        }],
    }

    return render_to_response(template_name, context, RequestContext(request))


def searchDetails(request, template_name, pk, page = None, query = None, items = None):
    results=''
    status_code = get_object_or_404(BuildFailure, pk=pk)
    build_failure = Info().getBFDetails(status_code.id)
    template = loader.get_template(template_name)
    c = RequestContext(request,  {'details' : build_failure, 'page' : page, 'query' : query, 'items' : items})
    return HttpResponse(template.render(c))

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
