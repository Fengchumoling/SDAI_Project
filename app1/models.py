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

    def __str__(self):
        return self.activity_name


class Task(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    text = models.CharField(blank=True, max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration = models.IntegerField()
    progress = models.FloatField()
    parent = models.CharField(max_length=100)


class Link(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    source = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    lag = models.IntegerField(blank=True, default=0)
