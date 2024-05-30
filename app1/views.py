import random
from datetime import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from .models import WBSElement, User, Group, Project, Task, Link
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from otherFiles.forms import *
from django.core.mail import send_mail


# Create your views here.

def index(request):
    # print(request.user)
    print(request.session['user_id'])
    user_id = request.session['user_id']
    group_projects = get_project_fun(user_id)
    return render(request, 'index.html', {'group_projects': group_projects})


def d3j(request):
    return render(request, 'd3j.html')


def gantt(request):
    return render(request, 'gantt.html')


def get_gantt_data(request):
    print("API")
    # data = {
    #     "tasks": [
    #         {"id": 1, "text": "Project #1", "start_date": "01-6-2024", "duration": 18},
    #         {"id": 2, "text": "Task #1", "start_date": "26-5-2024", "duration": 8, "parent": 1},
    #         {"id": 3, "text": "Task #2", "start_date": "01-5-2024", "duration": 8, "parent": 1}
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
    # print(request.POST.get('csrfmiddlewaretoken'))
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
        nativeeditor_status = request.GET.get('!nativeeditor_status')
        print(id)

        # start_date = datetime.strptime(start_date_str, '%d-%m-%Y %H:%M')
        # end_date = datetime.strptime(end_date_str, '%d-%m-%Y %H:%M')

        # task = Task.objects.create(
        #     id=id,
        #     text=text,
        #     start_date=start_date,
        #     end_date=end_date,
        #     duration=duration,
        #     progress=progress,
        #     parent=parent,
        #     project=project
        # )

        print(nativeeditor_status)
        print('success create task')
        # print(task)


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
# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         username = request.POST['name']
#         email = request.POST['email']
#         password = request.POST['password1']
#         # print(username, email, password)
#         if form.is_valid():
#             # user = form.save()
#             user = User.objects.create_user(email=email, name=username, password=password)
#             request.session['user_id'] = user.id
#             # login(request, user)
#             return redirect('index')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'register.html', {'form': form})

def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        sms_input = request.POST.get('sms')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not (password1 == password2):
            return render(request, 'register.html', {'error': "can not confirm password"})

        sms_code = request.session.get('sms_code')
        if not sms_code == sms_input:
            return render(request, 'register.html', {'error': "can not confirm sms code"})

        return redirect('index')

    return render(request, 'register.html')


def send_sms_code(email):
    sms_code = '%06d' % random.randint(0, 999999)
    EMAIL_FROM = "1690746478@qq.com"
    email_title = "Register"
    email_body = "Your sms code is %s" % sms_code
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    data = [send_status, sms_code]
    return data


def send_sms_code_view(request):
    email = request.GET.get('email')
    send_status, sms_code = send_sms_code(email)
    request.session['sms_code'] = sms_code
    return HttpResponse(send_status)


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


# Project Management
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


def get_project_fun(user_id):
    user = User.objects.get(id=user_id)
    groups = user.members.all()
    group_projects = []
    if groups is not None:
        for group in groups:
            project = group.project
            # members = group.members.all()
            # print(project)
            # group_projects.append((group, project, members))
            group_projects.append((group, project))
    return group_projects


def get_project(request):
    user_id = request.session['user_id']
    group_projects = get_project_fun(user_id)
    return render(request, 'project.html', {'group_projects': group_projects})


def project_detail(request, pid):
    # project = Project.objects.get(id=pid)
    # tasks = project.tasks.all()
    # links = project.links.all()
    request.session['project_id'] = pid
    # get_group_members(request)
    return redirect('gantt')


def group_detail(request, gid):
    return HttpResponse('This is the group detail view')


def get_group_members(request):
    # group_id = request.session['group_id']
    members_array = []
    project_id = request.session['project_id']
    project = Project.objects.get(id=project_id)
    group = project.group
    # group = Group.objects.get(id=group_id)
    members = group.members.all()
    for member in members:
        members_array.append({"key": member.email, "label": member.name})
    # opts = [
    #     {"key": 'a@c.com', "label": 'first user'},
    #     {'key': 'a@c.com', 'label': 'second user'},
    #     {'key': 'a@c.com', 'label': 'third user'},
    # ]
    return JsonResponse(members_array, safe=False)


# Chat Function

def chat_index(request):
    return render(request, 'chat_index.html')


def chat_room(request, room_name):
    # room_name = hashlib.md5(room_name.encode()).hexdigest()
    return render(request, 'chat_room.html', {
        'room_name': room_name,
    })


def once_task(request):
    # project_id = request.session['project_id']
    # project = Project.objects.get(id=1)
    # group = project.group
    # user = User.objects.get(id=3)
    # group.members.add(user)
    # return redirect('index')
    # ss = send_sms_code("1656296953@qq.com")
    # return HttpResponse(ss)

    # user = User.objects.create_user(email="test@a.com", name="test1", password="12345678")
    # request.session['user_id'] = user.id

    return redirect('index')

# Code miuvlfgmhregebed
