from django.db import models


# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=64)
    group = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Project(models.Model):
    project_name = models.CharField(max_length=50)
    project_activity = models.ForeignKey('Activity', on_delete=models.CASCADE)

    def __str__(self):
        return self.project_name


class Activity(models.Model):
    activity_name = models.CharField(max_length=20)
    activity_start_date = models.DateField()
    activity_end_date = models.DateField()
    activity_duration = models.DurationField()
    activity_resource = models.ManyToManyField('User')
    activity_progress = models.IntegerField(default=0)

    def __str__(self):
        return self.activity_name


class WBSElement(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
