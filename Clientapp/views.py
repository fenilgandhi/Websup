import threading , re
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
        message_form = Whatsapp_Message_Form(request.POST)
        mobile_numbers = request.POST["mobile_numbers"]
        mobile_numbers = re.findall( '\d{10}' , mobile_numbers)
        if len(mobile_numbers) < 1:
            errors = "No Valid Mobile Number Found"
        elif message_form.is_valid() :
            new_message = message_form.save(commit=False)
            new_message.from_user = request.user
            new_message.save()
            for mobile_number in mobile_numbers:
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