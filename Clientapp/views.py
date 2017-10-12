import threading, re
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from Clientapp.models import *
from Clientapp.forms import *
from Clientapp.yowsup_integration.stack import *


#####################
#   User Views
#####################
def dashboard(request):
    request.user.update_credits()
    plan_details = Whatsapp_Plans.objects.filter(is_active=True)
    user_plan_details = User_Plan.objects.filter(user=request.user).order_by('-id')
    if len(user_plan_details) > 0:
        user_plan_details = user_plan_details[0]
    template = "clientapp/dashboard.html"
    context = {'plan_details': plan_details, 'user_plan_details': user_plan_details}
    return render(request, template, context)


def send(request):
    Text_Formset = forms.modelformset_factory(Whatsapp_Text, form=Whatsapp_Text_Form, exclude=("format",), extra=3)
    Image_Formset = forms.modelformset_factory(Whatsapp_Image, exclude=("format",), extra=3)
    vCard_Formset = forms.modelformset_factory(Whatsapp_vCard, exclude=("format",), extra=3)

    text_formset = Text_Formset(prefix="text")
    image_formset = Image_Formset(prefix="image")
    vcard_formset = vCard_Formset(prefix="vcard")
    template = "clientapp/send.html"
    context = {'text_formset': text_formset, 'image_formset': image_formset, 'vcard_formset': vcard_formset}
    return render(request, template, context)

    # errors = None
    # if (request.method == "POST"):
    #     message_form = Whatsapp_New_Message_Form(request.POST, request.FILES)
    #     mobile_numbers = request.POST["mobile_numbers"]
    #     mobile_numbers = re.findall('\d{10}', mobile_numbers)
    #     if len(mobile_numbers) < 1:
    #         errors = "No Valid Mobile Number Found"
    #     if len(mobile_numbers) > request.user.remaining_credits:
    #         errors = "You do not have enough credits to send this message"
    #     elif message_form.is_valid():
    #         new_message = message_form.save(commit=False)
    #         new_message.user = request.user
    #         new_message.save()
    #         for mobile_number in mobile_numbers:
    #             mobile_number = '91' + mobile_number
    #             contact_detail = Whatsapp_Number.objects.filter(number=mobile_number)
    #             if len(contact_detail) < 1:
    #                 contact_detail = Whatsapp_Number()
    #                 contact_detail.number = mobile_number
    #                 contact_detail.save()
    #             else:
    #                 contact_detail = contact_detail[0]

    #             individual_message = Whatsapp_Individual_Message()
    #             individual_message.to_number = contact_detail
    #             individual_message.message_format = new_message
    #             individual_message.save()
    #             individual_message.message_format.user.queue_credit()
    #         return HttpResponseRedirect("/report")
    #     else:
    #         errors = str(message_form.errors)
    # message_form = Whatsapp_New_Message_Form()
    # template = "clientapp/send.html"
    # context = {"form": message_form, "errors": errors}
    # return render(request, template, context)


def report(request):
    individual_messages = Whatsapp_Individual_Message.objects.filter(message_format__user=request.user)
    template = "clientapp/report.html"
    context = {'individual_messages': individual_messages}
    return render(request, template, context)


def contactus(request):
    errors = None
    if (request.method == "POST"):
        contact_form = ContactusForm(request.POST)
        if contact_form.is_valid():
            new_contact = contact_form.save(commit=False)
            new_contact.from_user = request.user
            new_contact.save()
            return HttpResponseRedirect("/")
        else:
            errors = str(contact_form.errors)
    contact_form = ContactusForm()
    template = "clientapp/contactus.html"
    context = {'contact_form': contact_form, 'errors': errors}
    return render(request, template, context)


def adminReport(request):
    individual_messages = Whatsapp_Individual_Message.objects.all()
    template = "clientapp/adminReport.html"
    context = {'individual_messages': individual_messages}
    return render(request, template, context)

########################################################################################################################
#
#                          Adding  Yowsup   Integration
#
# #######################################################################################################################
yowsup_handler = YowsupWebStack()

# Starting the Whatsapp Stack Loop in a new thread.
threading.Thread(target=yowsup_handler.start).start()

# Access to yowsupweb layer
weblayer = yowsup_handler.get_web_layer()


def api(request, command):
    if command == 'login':
        if not weblayer.assertConnected():
            weblayer.login('917016034770', 'XfZURrqRo/0eC2+v16D29xstqBQ=')

    if command == 'connection_status':
        return HttpResponse( weblayer.assertConnected() )

    if (command == 'send'):
        id = request.GET.get('id', '')
        if len(id) < 1:
            return HttpResponse(False)
        msg_object = Whatsapp_Individual_Message.objects.filter(delivery_status=0, id=id)
        if (len(msg_object) > 0):
            msg_object = msg_object[0]
            weblayer.send_message(msg_object)
            return HttpResponse(True)
    # Default Case if nothing else works
    return HttpResponse(False)


def api_mainpage(request, id=None):
    if id is None:
        msg_formats = Whatsapp_Message_Format.objects.filter(user__is_active=True, whatsapp_individual_message__delivery_status=0).distinct()
        template = "clientapp/whatsapp_mainpage.html"
        context = {'msg_formats': msg_formats}
        return render(request, template, context)
    else:
        individual_messages = Whatsapp_Individual_Message.objects.filter(message_format__id=id, delivery_status=0)
        contacts = [msg.to_number.number for msg in individual_messages]
        weblayer.contacts_sync(contacts)
        template = "clientapp/whatsapp_message.html"
        context = {'messages': individual_messages}
        return render(request, template, context)
