import random
from datetime import datetime
from django.utils import timezone

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from .models import WBSElement, Group, Project, Task, Link
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from otherFiles.forms import *
from django.core.mail import send_mail


# Create your views here.

@login_required
def index(request):
    user = request.user
    group_projects = get_project_fun(user)
    user_tasks = user.tasks.all()
    now = timezone.now()

    past_tasks = user_tasks.filter(end_date__lt=now)
    current_tasks = user_tasks.filter(start_date__lt=now, end_date__gt=now)
    future_tasks = user_tasks.filter(start_date__gt=now)

    tasks_count_all = user_tasks.count()
    tasks_count_past = past_tasks.count()
    tasks_count_current = current_tasks.count()
    tasks_count_future = future_tasks.count()

    latest_task = user_tasks.order_by('-end_date').first()
    if latest_task:
        days_remaining = (latest_task.end_date - now).days
    else:
        days_remaining = 0

    overlapping_tasks = []

    for i, task1 in enumerate(user_tasks):
        for task2 in user_tasks[i + 1:]:
            if (task1.start_date < task2.end_date) and (task2.start_date < task1.end_date):
                overlapping_tasks.append((task1, task2))

    if overlapping_tasks:
        overlapping_content = ''
        for task1, task2 in overlapping_tasks:
            s = f'({task1.text}, {task2.text}),'
            overlapping_content += s
        overlapping_content += 'these tasks have conflicting schedules.'
    else:
        overlapping_content = 'The next schedule is reasonable and there is no duplication of tasks.'

    context = {
        'group_projects': group_projects,
        'user': user,
        'user_tasks': user_tasks,
        'tasks_count_all': tasks_count_all,
        'tasks_count_past': tasks_count_past,
        'tasks_count_current': tasks_count_current,
        'tasks_count_future': tasks_count_future,
        'days_remaining': days_remaining,
        'overlapping_content': overlapping_content
    }
    return render(request, 'index.html', context=context)


def d3j(request):
    return render(request, 'd3j.html')


def gantt(request):
    return render(request, 'gantt2.html')


def get_gantt_data(request):
    print("API")

    project = Project.objects.get(id=request.session['project_id'])
    tasks = project.tasks.all()
    links = project.links.all()

    tasks_data = []
    for task in tasks:
        task_data = {
            "id": task.id,
            "text": task.text,
            "start_date": task.start_date.strftime('%d-%m-%Y'),
            "duration": task.duration,
            "parent": task.parent,
            "progress": task.progress,
            "Holder": task.holder.username
        }
        tasks_data.append(task_data)

    links_data = []
    for link in links:
        link_data = {
            "id": link.id,
            "source": link.source,
            "target": link.target,
            "type": link.type,
        }
        links_data.append(link_data)

    data = {
        "tasks": tasks_data,
        "links": links_data
    }

    # print(tasks)
    # print(links)

    return JsonResponse(data)


def change_gantt_data(request):
    # print("Change GanttData")
    # print(request.POST.get('csrfmiddlewaretoken'))
    editing = request.GET.get('editing')
    gantt_mode = request.GET.get('gantt_mode')

    project_id = request.session['project_id']
    project = Project.objects.get(id=project_id)
    group = project.group
    control = group.control
    current_user = request.user

    if current_user != control:
        return HttpResponse('You are not allowed to change gantt data')

    if gantt_mode == "tasks":
        id = request.POST.get('id')
        start_date_str = request.POST.get('start_date')
        text = request.POST.get('text')
        duration = request.POST.get('duration')
        end_date_str = request.POST.get('end_date')
        progress = request.POST.get('progress')
        parent = request.POST.get('parent')
        holder_name = request.POST.get('Holder')
        nativeeditor_status = request.POST.get('!nativeeditor_status')

        # print(type(progress))

        start_date = datetime.strptime(start_date_str, '%d-%m-%Y %H:%M')
        end_date = datetime.strptime(end_date_str, '%d-%m-%Y %H:%M')

        holder_user = User.objects.get(username=holder_name)
        progress_float = round(float(progress), 2)

        if nativeeditor_status == "inserted" or nativeeditor_status == "updated":
            task, created = Task.objects.update_or_create(
                id=id,
                defaults={
                    'text': text,
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration': duration,
                    'progress': progress_float,
                    'parent': parent,
                    'project': project,
                    'holder': holder_user
                }
            )
            return HttpResponse('Task added')

        elif nativeeditor_status == "deleted":
            res = {'status': "ok"}
            return JsonResponse(res)

    elif gantt_mode == "links":
        source = request.POST.get('source')
        target = request.POST.get('target')
        type = request.POST.get('type')
        id = request.POST.get('id')
        nativeeditor_status = request.POST.get('!nativeeditor_status')
        if nativeeditor_status == "inserted" or nativeeditor_status == "updated":
            link, created = Link.objects.update_or_create(
                id=id,
                defaults={
                    'source': source,
                    'target': target,
                    'type': type,
                    'project': project,
                }
            )

        return HttpResponse('Link added')

    else:
        return HttpResponse('error')

    return HttpResponse('error')


def gantt_delete_task(request):
    project_id = request.session['project_id']
    project = Project.objects.get(id=project_id)
    group = project.group
    control = group.control
    current_user = request.user

    if current_user != control:
        res = {'status': "false"}
        return JsonResponse(res)

    task_id = request.POST.get('id')
    task = Task.objects.get(id=task_id)
    task.delete()
    res = {'status': "ok"}
    return JsonResponse(res)


def gantt_delete_link(request):
    project_id = request.session['project_id']
    project = Project.objects.get(id=project_id)
    group = project.group
    control = group.control
    current_user = request.user

    if current_user != control:
        res = {'status': "false"}
        return JsonResponse(res)

    link_id = request.POST.get('id')
    link = Link.objects.get(id=link_id)
    link.delete()
    res = {'status': "ok"}
    return JsonResponse(res)


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

        user = User.objects.create_user(username=username, password=password1, email=email)
        login(request, user)
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
    # email = '1656296953@qq.com'
    send_status, sms_code = send_sms_code(email)
    request.session['sms_code'] = sms_code
    return HttpResponse(send_status)


def login_view(request):
    if request.method == 'POST':
        # email = request.POST['email']
        username = request.POST.get('username')
        password = request.POST.get('password')
        # username = 'test1'
        # password = '12345678'
        # print(email, password)
        # user = authenticate(request, email=email, password=password)
        user = authenticate(username=username, password=password)
        # user = User.objects.get(email=email)
        # if user.check_password(password):
        if user:
            # print("Login Successful")
            login(request, user)
            request.session['user_id'] = user.id
            # print(request.user.name, request.user.id)
            return redirect('index')
        else:
            print('login fail')
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    else:
        # print(request.user)
        return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('index')


# Project Management
def project_create(request):
    if request.method == 'POST':
        project_name = request.POST['project_name']
        group_name = request.POST['group_name']
        # user_id = request.session['user_id']
        # user = User.objects.get(id=user_id)
        user = request.user

        print(project_name, group_name, user)

        group = Group.objects.create(name=group_name, control=user)
        group.members.add(user)
        project = Project.objects.create(name=project_name, group=group)

        return redirect('index')

    else:
        # print(request.user, request.session['user_id'])
        return render(request, 'project_create.html')


def get_project_fun(user):
    # user = User.objects.get(id=user_id)
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
    # user_id = request.session['user_id']
    user = request.user
    group_projects = get_project_fun(user)
    return render(request, 'project.html', {'group_projects': group_projects})


def project_detail(request, pid):
    # project = Project.objects.get(id=pid)
    # tasks = project.tasks.all()
    # links = project.links.all()
    request.session['project_id'] = pid
    # get_group_members(request)
    return redirect('gantt')


def group_detail(request, gid):
    group = Group.objects.get(id=gid)
    project = group.project
    request.session['project_id'] = project.id
    control = group.control
    members = group.members.all()
    now = timezone.now()
    project_tasks = project.tasks.all()

    earliest_task = project_tasks.order_by('start_date').first()
    latest_task = project_tasks.order_by('-end_date').first()

    if earliest_task:
        project_start_date = earliest_task.start_date
    else:
        project_start_date = ''

    if latest_task:
        days_remaining = (latest_task.end_date - now).days
        project_end_date = latest_task.end_date
    else:
        project_end_date = ''
        days_remaining = 0

    past_tasks = project_tasks.filter(end_date__lt=now)
    current_tasks = project_tasks.filter(start_date__lt=now, end_date__gt=now)
    future_tasks = project_tasks.filter(start_date__gt=now)

    tasks_count_all = project_tasks.count()
    tasks_count_past = past_tasks.count()
    tasks_count_current = current_tasks.count()
    tasks_count_future = future_tasks.count()

    abnormal_content = ''
    abnormal_tasks = []
    for task in past_tasks:
        if task.progress != 1:
            abnormal_tasks.append(task)

    if abnormal_tasks:
        abnormal_content += 'Abnormal tasks: '
        for task in abnormal_tasks:
            abnormal_content += f'{task.text},'
        abnormal_content += ' please handle it as soon as possible.'
    else:
        abnormal_content = 'The project is progressing normally and the task has ended normally.'

    context = {
        'group': group,
        'control': control,
        'members': members,
        'project_start_date': project_start_date,
        'project_end_date': project_end_date,
        'tasks_count_all': tasks_count_all,
        'tasks_count_past': tasks_count_past,
        'tasks_count_current': tasks_count_current,
        'tasks_count_future': tasks_count_future,
        'abnormal_content': abnormal_content,
        'days_remaining': days_remaining,
    }
    return render(request, 'group.html', context=context)


def get_group_members(request):
    # group_id = request.session['group_id']
    members_array = []
    project_id = request.session['project_id']
    project = Project.objects.get(id=project_id)
    group = project.group
    # group = Group.objects.get(id=group_id)
    members = group.members.all()
    for member in members:
        members_array.append({"key": member.username, "label": member.username})
    # opts = [
    #     {"key": 'a@c.com', "label": 'first user'},
    #     {'key': 'a@c.com', 'label': 'second user'},
    #     {'key': 'a@c.com', 'label': 'third user'},
    # ]
    return JsonResponse(members_array, safe=False)


def add_group_member(request, gid):
    if request.method == "POST":
        # return HttpResponse("success")
        username = request.POST['username']

        user_check = User.objects.filter(username=username)
        print(user_check.exists())
        if not user_check.exists():
            return JsonResponse({'msg': 'There is no such user'})

        user_add = User.objects.get(username=username)

        if user_add:
            group = Group.objects.get(id=gid)
            current_user = request.user
            control = group.control
            if user_add in group.members.all():
                return JsonResponse({'msg': "The user is already in the group"})
            if current_user == control:
                group.members.add(user_add)
                return JsonResponse({'msg': 'success'})
            else:
                return JsonResponse({'msg': 'You are not allowed to add a member'})
        else:
            return JsonResponse({'msg': 'There is no such user'})
    else:
        return JsonResponse({'msg': 'illegal access'})


def delete_group_member(request, gid, uid):
    group = Group.objects.get(id=gid)
    current_user = request.user
    control = group.control
    target_url = '/group/{}'.format(gid)
    if current_user == control:
        user_remove = User.objects.get(id=uid)
        group.members.remove(user_remove)
        return redirect(target_url)
    else:
        return redirect(target_url)


def group_delete(request, pid):
    group = Group.objects.get(id=pid)
    project = group.project
    control = group.control
    if request.user == control:
        project.delete()
        group.delete()
        print("success delete")
        return redirect('index')
    else:
        return redirect('index')


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

    # user1 = request.user
    # user1 = User.objects.create_user(email="test1@a.com", name="test1", password="12345678")
    # user2 = User.objects.create_user(email="test2@a.com", username="test2", password="12345678")
    # user3 = User.objects.create_user(email="test3@a.com", username="test3", password="12345678")
    # user4 = User.objects.create_user(email="test4@a.com", username="test4", password="12345678")
    # user5 = User.objects.create_user(email="test5@a.com", username="test5", password="12345678")

    # request.session['user_id'] = user1.id

    # user1 = User.objects.get(id=request.session['user_id'])
    # user2 = User.objects.get(id=2)
    # user3 = User.objects.get(id=3)
    # user4 = User.objects.get(id=4)
    # user5 = User.objects.get(id=5)
    #
    # group1 = Group.objects.create(name="First Group", control=user1)
    # group1 = Group.objects.get(id=1)
    # group1.members.add(user2, user3)
    # project1 = Project.objects.create(name="User Management System", group=group1)
    #
    # group2 = Group.objects.create(name="Group 2", control=user1)
    # group2.members.add(user4, user5)
    # project2 = Project.objects.create(name="User Management System", group=group2)

    group2 = Group.objects.get(id=2)

    return redirect('index')

# Code miuvlfgmhregebed
