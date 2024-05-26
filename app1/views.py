from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.http import JsonResponse
from .models import WBSElement
from django.views import View

import hashlib

# Create your views here.

def index(request):
    return render(request, 'index.html')


def d3j(request):
    return render(request, 'd3j.html')

def gantt(request):
    return render(request, 'gantt.html')


def getGanttData(request):
    print("API")
    data = {
        "tasks": [
            {"id": 1, "text": "Project #1", "start_date": "01-04-2024", "duration": 18, 'progress': 0.5},
            {"id": 2, "text": "Task #1", "start_date": "02-04-2024", "duration": 8, "parent": 1, 'progress': 0.4},
            {"id": 3, "text": "Task #2", "start_date": "11-04-2024", "duration": 8, "parent": 1, 'progress': 1},
        ],
        "links": [
            {"id": 1, "source": 1, "target": 2, "type": "1"},
            {"id": 2, "source": 2, "target": 3, "type": "0"}
        ]
    }
    return JsonResponse(data)


def changeGanttData(request):
    print("Change GanttData")
    data = request.GET.get('id')
    print(data)
    return HttpResponse("Change GanttData")



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

def chat_index(request):
    return render(request, 'chat_index.html')


def room(request, room_name):
    # room_name = hashlib.md5(room_name.encode()).hexdigest()
    return render(request, 'room.html', {
        'room_name': room_name,
    })