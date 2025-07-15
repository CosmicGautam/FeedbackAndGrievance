from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

departments = [
    {'id':1, 'name':'DoTM'},
    {'id':2, 'name':'Foreign Affairs'},
    {'id':3, 'name':'Sirjanship Sewa'},
]

def home(request):
    context = {'departments': departments}
    return render(request, 'base/home.html', context)

def department(request, pk):
    department = None
    for i in departments:
        if i['id'] == int(pk):
            department = i
    context  = {'department': department}
    return render(request,'base/department.html', context)