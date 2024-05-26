from datetime import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from .models import WBSElement, User, Group, Project, Task, Link
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from otherFiles.forms import *


# Create your views here.

def index(request):
    # print(request.user)
    print(request.session['user_id'])
    return render(request, 'index.html')


def d3j(request):
    return render(request, 'd3j.html')


def gantt(request):
    return render(request, 'gantt.html')


def get_gantt_data(request):
    print("API")
    # data = {
    #     "tasks": [
    #         {"id": 1, "text": "Project #1", "start_date": "01-04-2020", "duration": 18},
    #         {"id": 2, "text": "Task #1", "start_date": "02-04-2020", "duration": 8, "parent": 1},
    #         {"id": 3, "text": "Task #2", "start_date": "11-04-2020", "duration": 8, "parent": 1}
    #     ],
    #     "links": [
    #         {"id": 1, "source": 1, "target": 2, "type": "1"},
    #         {"id": 2, "source": 2, "target": 3, "type": "0"}
    #     ]
    # }

    project = Project.objects.get(id=request.session['project_id'])
    tasks = project.tasks.all()
    links = project.links.all()
    # # 获取所有任务(Task)和链接(Link)对象
    # tasks = Task.objects.all()
    # links = Link.objects.all()

    # 构建任务(Task)数据列表
    tasks_data = []
    for task in tasks:
        task_data = {
            "id": task.id,
            "text": task.text,
            "start_date": task.start_date.strftime('%d-%m-%Y'),
            "duration": task.duration,
            "parent": task.parent,
            # 如果需要，可以添加其他字段
        }
        tasks_data.append(task_data)

    # 构建链接(Link)数据列表
    links_data = []
    for link in links:
        link_data = {
            "id": link.id,
            "source": link.source,
            "target": link.target,
            "type": link.type,
            # 如果需要，可以添加其他字段
        }
        links_data.append(link_data)

    # 构建包含任务和链接的数据字典
    data = {
        "tasks": tasks_data,
        "links": links_data
    }

    print(tasks)
    print(links)

    return JsonResponse(data)


def change_gantt_data(request):
    print("Change GanttData")
    editing = request.GET.get('editing')
    gantt_mode = request.GET.get('gantt_mode')

    project_id = request.session['project_id']
    project = Project.objects.get(id=project_id)

    if gantt_mode == "tasks":
        id = request.GET.get('id')
        start_date_str = request.GET.get('start_date')
        text = request.GET.get('text')
        duration = request.GET.get('duration')
        end_date_str = request.GET.get('end_date')
        progress = request.GET.get('progress')
        parent = request.GET.get('parent')
        holder = request.GET.get('Holder')
        nativeeditor_status = request.GET.get('nativeeditor_status')
        print(id)

        start_date = datetime.strptime(start_date_str, '%d-%m-%Y %H:%M')
        end_date = datetime.strptime(end_date_str, '%d-%m-%Y %H:%M')

        task = Task.objects.create(
            id=id,
            text=text,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            progress=progress,
            parent=parent,
            project=project
        )

        print('success create task')
        print(task)


    elif gantt_mode == "links":
        pass
    else:
        pass

    # print(data)
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


# User Management System
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password1']
        # print(username, email, password)
        if form.is_valid():
            # user = form.save()
            user = User.objects.create_user(email=email, name=username, password=password)
            request.session['user_id'] = user.id
            # login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)
        # user = authenticate(request, email=email, password=password)
        user = User.objects.get(email=email)
        if user.check_password(password):
            # print("Login Successful")
            # login(request, user)
            request.session['user_id'] = user.id
            # print(request.user.name, request.user.id)
            return redirect('index')
        else:
            print('login fail')
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    else:
        # print(request.user)
        return render(request, 'login.html')


def project_create(request):
    if request.method == 'POST':
        project_name = request.POST['project_name']
        group_name = request.POST['group_name']
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)

        print(project_name, group_name, user)

        group = Group.objects.create(name=group_name, control=user)
        group.members.add(user)
        project = Project.objects.create(name=project_name, group=group)

        return redirect('index')

    else:
        # print(request.user, request.session['user_id'])
        return render(request, 'project_create.html')


def get_project(request):
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    groups = user.members.all()
    group_projects = []
    if groups is not None:
        for group in groups:
            project = group.project
            print(project)
            group_projects.append((group, project))
    return render(request, 'project.html', {'group_projects': group_projects})


def project_detail(request, pid):
    # project = Project.objects.get(id=pid)
    # tasks = project.tasks.all()
    # links = project.links.all()
    request.session['project_id'] = pid
    return redirect('gantt')


def group_detail(request, gid):
    return HttpResponse('This is the group detail view')
