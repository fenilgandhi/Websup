import threading
from django.shortcuts import render, HttpResponseRedirect , HttpResponse
from .models import *
from .yowsup_integration.stack import *

# Create your views here.
#####################
#   User Views
#####################
def dashboard(request):
    user = request.user
    template = "clientapp/dashboard.html"
    context = {'user' : user}
    return render(request, template, context)

def send(request):
    errors = None
    if (request.method == "POST"):
        message_form = Whatsapp_Message_Form(request.POST, request.FILES)
        if message_form.is_valid():
            new_message = message_form.save(commit=False)
            new_message.handled_by = request.user
            new_message.save()
            return HttpResponseRedirect("/send")
        else:
            errors = str(new_member_form.errors)
    message_form = Whatsapp_Message_Form()
    template = "clientapp/send.html"
    context = {"form": message_form, "errors": errors}
    return render(request, template, context)


def report(request):
    template = "clientapp/report.html"
    context = {}
    return render(request, template, context)


##########################################################################################################################                
#                   
#                          Adding  Yowsup   Integration 
#
##########################################################################################################################
yowsup_handler = YowsupWebStack()

## Starting the Whatsapp Stack Loop in a new thread. 
#threading.Thread(target=yowsup_handler.start).start()

## Access to yowsupweb layer
weblayer = yowsup_handler.get_web_layer()
weblayer.login( '919999999999' , '9999999999999999999999999999')    

def api(request, command):
    if command == 'send':
        for token in 'If you are reading this message, then the demo is live.'.split(' '):
            weblayer.message_send('919999999999' , token)
    return HttpResponse("Done")

def api_gui(request):
    template = "clientapp/whatsapp.html"
    context = {}
    return render(request, template, context)