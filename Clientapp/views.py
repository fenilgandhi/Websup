from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
	template = "clientapp_dashboard.html"
	context = {}
	return render(request , template,context )

def aboutus(request):
	template = "clientapp_dashboard.html"
	context = {}
	return render(request , template,context )

def plans(request):
	template = "clientapp_dashboard.html"
	context = {}
	return render(request , template,context )

def contactus(request):
	template = "clientapp_dashboard.html"
	context = {}
	return render(request , template,context )

@login_required
def send(request):
	template = "clientapp_dashboard.html"
	context = {}
	return render(request , template,context )

@login_required
def report(request):
	template = "clientapp_dashboard.html"
	context = {}
	return render(request , template,context )