from django.db import models


# Create your models here.

#Create a user model, store user information for login, chat room use, and permission control
class User(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=64)
    group = models.IntegerField(default=0)

    def __str__(self):
        return self.name


#The model that creates the project stores the Task and name of the project
class Project(models.Model):
    project_name = models.CharField(max_length=50)
    project_activity = models.ForeignKey('Activity', on_delete=models.CASCADE)

    def __str__(self):
        return self.project_name


#The model that creates the Task(Activity) stores the information about each Tasks
class Activity(models.Model):
    activity_name = models.CharField(max_length=20)
    activity_start_date = models.DateField()
    activity_end_date = models.DateField()
    activity_duration = models.DurationField()
    activity_resource = models.ManyToManyField('User')
    activity_progress = models.IntegerField(default=0)

    def __str__(self):
        return self.activity_name


#The model is used to store the content and logic of the WBS diagram
class WBSElement(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
