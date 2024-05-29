"""
URL configuration for SDAI_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app1.views import *
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("admin/", admin.site.urls),

    path("index/", index, name="index"),
    path("", index, name="home"),
    path("d3j/", d3j),
    path("gantt/", gantt),

    path("getGanttData/", get_gantt_data),
    path("changeGanttData/", change_gantt_data),
    path("gantt/", gantt, name='gantt'),
    path('wbs_tool/', wbs_tool, name='wbs_tool'),
    path('get-wbs-data/', get_wbs_data, name='get_wbs_data'),

    # User Management System
    path("register/", register, name='register'),
    path("login/", login_view, name='login'),
    path("sendsms/", send_sms_code_view),


    # Project management
    path("project/create", project_create),
    path("project/", get_project),
    path("project/<int:pid>", project_detail, name='project_detail'),

    # Group Management
    path("group/<int:gid>/", group_detail, name='group_detail'),
    path("getMemberData/", get_group_members, name='get_group_members'),


    # Chat Function
    path("chat/", chat_index, name='chat_index'),
    path("chat/<str:room_name>/", chat_room, name='chat_room'),

    path("set/", once_task),
]
