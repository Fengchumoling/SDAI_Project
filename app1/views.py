from django.shortcuts import render
from django.http import JsonResponse
from .models import WBSElement


# Create your views here.

def index(request):
    return render(request, 'index.html')


def d3j(request):
    return render(request, 'd3j.html')


def gantt(request):
    return render(request, 'gantt.html')


def get_wbs_data(request):
    data = []
    for element in WBSElement.objects.all():
        node = {
            'id': element.id,
            'text': element.name,
            'parent': element.parent_id if element.parent else '#'
        }
        data.append(node)
    return JsonResponse(data, safe=False)


def wbs_tool(request):
    return render(request, 'wbs_tool.html')
