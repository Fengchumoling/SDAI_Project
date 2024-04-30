from django.shortcuts import render


# Create your views here.

def index(request):
    return render(request, 'index.html')

def d3j(request):
    return render(request, 'd3j.html')
