import datetime
import threading , re
from .models import *

from django.shortcuts import render, HttpResponseRedirect , HttpResponse, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404
from django.template import loader
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.debug import sensitive_post_parameters


from .yowsup_integration.stack import *

# Create your views here.
#####################
#   User Views
#####################
def dashboard(request):
	plan_details = Plan.objects.filter(is_active=True)
	user = request.user
	template = "clientapp/dashboard.html"
	context = {'user' : user, 'plan_details' : plan_details}
	return render(request, template, context)

def send(request):
	errors = None
	if (request.method == "POST"):
		message_form = Whatsapp_Message_Form(request.POST)
		mobile_numbers = request.POST["mobile_numbers"]
		mobile_numbers = re.findall( '\d{10}' , mobile_numbers)
		if len(mobile_numbers) < 1:
			errors = "No Valid Mobile Number Found"
		if len(mobile_numbers) > request.user.remaining_credits :
			errors = "You do not have enough credits to send this message"
		elif message_form.is_valid() :
			new_message = message_form.save(commit=False)
			new_message.from_user = request.user
			new_message.save()
			for mobile_number in mobile_numbers:
				mobile_number = '91' + mobile_number
				contact_detail = Contact.objects.filter(number=mobile_number)
				if len(contact_detail) < 1:
					contact_detail = Contact()
					contact_detail.number = mobile_number
					contact_detail.save()
				else:
					contact_detail = contact_detail[0]

				individual_message = WhatsApp_Individual_Message()
				individual_message.to_contact = contact_detail
				individual_message.message_format = new_message
				individual_message.save()
			return HttpResponseRedirect("/report")
		else:
			errors = str(new_member_form.errors)
	message_form = Whatsapp_Message_Form()
	template = "clientapp/send.html"
	context = {"form": message_form, "errors": errors}
	return render(request, template, context)


def report(request):
	individual_messages = WhatsApp_Individual_Message.objects.filter(message_format__from_user=request.user)
	template = "clientapp/report.html"
	context = { 'individual_messages' : individual_messages}
	return render(request, template, context)

##########################################################################################################################                
#                   
#                          Adding  Yowsup   Integration 
#
##########################################################################################################################
yowsup_handler = YowsupWebStack()

## Starting the Whatsapp Stack Loop in a new thread. 
threading.Thread(target=yowsup_handler.start).start()

## Access to yowsupweb layer
weblayer = yowsup_handler.get_web_layer()
weblayer.login( '917016034770' , 'kbjsCUt9oB33CbnU0OlcQaXU6F0=')    

def api(request, command):
	if command == 'status':
		if weblayer.assertConnected():
			return HttpResponse(True)
		else:
			weblayer.login( '917016034770' , 'kbjsCUt9oB33CbnU0OlcQaXU6F0=')
			if weblayer.assertConnected():
				return HttpResponse(True)			
	
	if (command == 'send'):
		id = request.GET['id']
		msg_object = WhatsApp_Individual_Message.objects.filter(delivered=False , id=id)
		if len(msg_object) > 0 :
			msg_object= msg_object[0]
			if weblayer.message_send(msg_object.to_contact.number, msg_object.message_format.msg_text):
				msg_object.delivered=True
				msg_object.save()
				return HttpResponse(True)

	## Default Case if nothing else works
	return HttpResponse(False)

def api_mainpage(request, id=None):
	if id == None:
		msg_formats = WhatsApp_Message_Format.objects.filter(from_user__is_active=True, whatsapp_individual_message__delivered=False).distinct()
		template = "clientapp/whatsapp_mainpage.html"
		context = { 'msg_formats' : msg_formats }
		return render(request, template, context)
	else:
		individual_messages = WhatsApp_Individual_Message.objects.filter(message_format__id=id , delivered=False)
		contacts = [msg.to_contact.number for msg in individual_messages]
		weblayer.contacts_sync(contacts)
		template = "clientapp/whatsapp_message.html"
		context = { 'messages' : individual_messages }
		return render(request, template, context)