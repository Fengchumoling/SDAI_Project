from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(
            email=email,
            name=name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Group(models.Model):
    name = models.CharField(max_length=255)
    control = models.ForeignKey(User, related_name='controlled_groups', on_delete=models.SET_NULL, null=True,
                                blank=True)
    members = models.ManyToManyField(User, related_name='members')

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255, default="Project Name")
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='project', default=None, null=True)

    def __str__(self):
        return self.name

    # def __str__(self):
    #     return self.activity_name


class Task(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    text = models.CharField(blank=True, max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration = models.IntegerField()
    progress = models.FloatField()
    parent = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')


class Link(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    source = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    lag = models.IntegerField(blank=True, default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='links')


class WBSElement(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
