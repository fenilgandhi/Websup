from django.shortcuts import render, HttpResponseRedirect , get_object_or_404 ,HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
	template = "clientapp_dashboard.html"
	context = {}
	return render(request , template,context )

def aboutus(request):
	template = "clientapp_aboutus.html"
	context = {}
	return render(request , template,context )

def plans(request):
	template = "clientapp_plans.html"
	context = {}
	return render(request , template,context )

def contactus(request):
	template = "clientapp_contactus.html"
	context = {}
	return render(request , template,context )

@login_required
def send(request):
	errors = None
	if (request.method == "POST"):
		message_form = Whatsapp_Message_Form(request.POST , request.FILES)
		if message_form.is_valid():
			new_message = message_form.save(commit=False)
			new_message.handled_by = request.user
			new_message.save()
			return HttpResponseRedirect("/send")
		else:
			errors = str(new_member_form.errors)
	message_form = Whatsapp_Message_Form()
	template = "clientapp_send.html"
	context = {"form" : message_form , "errors" : errors}
	return render(request , template, context )


@login_required
def report(request):
	template = "clientapp_report.html"
	context = {}
	return render(request , template,context )