from django.shortcuts import render, HttpResponse
from django.http import JsonResponse


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
            {"id": 1, "text": "Project #1", "start_date": "01-04-2020", "duration": 18},
            {"id": 2, "text": "Task #1", "start_date": "02-04-2020", "duration": 8, "parent": 1},
            {"id": 3, "text": "Task #2", "start_date": "11-04-2020", "duration": 8, "parent": 1}
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
