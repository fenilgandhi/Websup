import threading
import re
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from Clientapp.models import *
from Clientapp.forms import *
from Clientapp.yowsup_integration.stack import *

#####################
#   User Views
#####################
def dashboard(request):
    request.user.update_credits()
    plan_details = Whatsapp_Plan.objects.filter(is_active=True)
    user_plan_details = User_Plan.objects.filter(user=request.user).order_by('-id')
    if len(user_plan_details) > 0:
        user_plan_details = user_plan_details[0]
    template = "clientapp/dashboard.html"
    context = {'plan_details': plan_details, 'user_plan_details': user_plan_details}
    return render(request, template, context)


def send(request):
    errors = None
    Text_Formset = forms.formset_factory(Whatsapp_Text_Form, extra=1)
    Image_Formset = forms.formset_factory(Whatsapp_Image_Form, extra=1)
    #vCard_Formset = forms.formset_factory(Whatsapp_vCard_Form, extra=1)

    if (request.method == "POST"):
        message_form = Whatsapp_New_Message_Form(request.POST, request.FILES)
        text_formset = Text_Formset(request.POST, prefix="text")
        image_formset = Image_Formset(request.POST, request.FILES, prefix="image")
     #   vcard_formset = vCard_Formset(request.POST, prefix="vcard")
        mobile_numbers = request.POST["mobile_numbers"]
        mobile_numbers = re.findall('\d{10}', mobile_numbers)
        if len(mobile_numbers) < 1:
            errors = "No Valid Mobile Number Found"
        elif message_form.is_valid() and text_formset.is_valid():
            ##########################################################################
            #   Validate and get proper Mobile numbers
            ##########################################################################
            contacts = []
            for mobile_number in mobile_numbers:
                mobile_number = '91' + mobile_number
                mobile_number_object = Whatsapp_Number.objects.filter(number=mobile_number)
                if len(mobile_number_object) < 1:
                    mobile_number_object = Whatsapp_Number()
                    mobile_number_object.number = mobile_number
                    mobile_number_object.save()
                else:
                    mobile_number_object = mobile_number_object[0]
                contacts.append(mobile_number_object)

            ##########################################################################
            #   Generate Db Objects from formsets using commit=False
            ##########################################################################
            new_message_format = message_form.save(commit=False)
            credits = request.user.remaining_credits
            len_contacts = len(contacts)

            # Saving details for Message_Format
            new_message_format.user = request.user
            new_message_format.save()
            new_message_format.mobile_numbers.add(*contacts)

            # Saving each text message
            for text_form in text_formset:
                text_message = text_form.save(commit=False)
                text_message.format = new_message_format
                if len(text_message.text) > 0:
                    text_message.save()
                    if credits < len_contacts: continue
                    else: credits -= len_contacts
                    for contact in contacts:
                        whatsapp_text_delivery = Text_Delivery()
                        whatsapp_text_delivery.to_number = contact
                        whatsapp_text_delivery.message_text = text_message
                        whatsapp_text_delivery.message_format = new_message_format
                        whatsapp_text_delivery.save()

            # Saving each image message
            for image_form in image_formset:
                image_message = image_form.save(commit=False)
                image_message.format = new_message_format
                if bool(image_message.image):
                    image_message.save()
                    if credits < len_contacts: continue
                    else: credits -= len_contacts
                    for contact in contacts:
                        whatsapp_image_delivery = Image_Delivery()
                        whatsapp_image_delivery.to_number = contact
                        whatsapp_image_delivery.message_image = image_message
                        whatsapp_image_delivery.message_format = new_message_format
                        whatsapp_image_delivery.save()

            # Saving each vcard message
            # for vcard_form in vcard_formset:
            #     vcard_message = vcard_form.save(commit=False)
            #     vcard_message.format = new_message_format
            #     if len(vcard_message.name) > 0:
            #         vcard_message.save()
            #         if credits < len_contacts: continue
            #         else: credits -=  len_contacts
            #         for contact in contacts:
            #             whatsapp_vcard_delivery = vCard_Delivery()
            #             whatsapp_vcard_delivery.to_number = contact
            #             whatsapp_vcard_delivery.message = vcard_message
            #             whatsapp_vcard_delivery.message_format = new_message_format
            #             whatsapp_vcard_delivery.save()

            request.user.update_credits()
            return HttpResponseRedirect("/report")
        else:
            errors = message_form.errors + text_formset.errors

    else:
        message_form = Whatsapp_New_Message_Form()

    text_formset = Text_Formset(prefix="text")
    image_formset = Image_Formset(prefix="image")
    #vcard_formset = vCard_Formset(prefix="vcard")

    template = "clientapp/send.html"
    context = {
        'message_form': message_form,
        'text_formset': text_formset,
        'image_formset': image_formset,
     #   'vcard_formset': vcard_formset,
        'errors': errors
    }
    return render(request, template, context)


def report(request):
    individual_messages = Delivery_Status.objects.all().order_by('-added_on')
    template = "clientapp/report.html"
    context = {'individual_messages': individual_messages}
    return render(request, template, context)


def contactus(request):
    errors = None
    if (request.method == "POST"):
        contact_form = Contactus_Form(request.POST)
        if contact_form.is_valid():
            new_contact = contact_form.save(commit=False)
            new_contact.from_user = request.user
            new_contact.save()
            return HttpResponseRedirect("/")
        else:
            errors = str(contact_form.errors)
    contact_form = Contactus_Form()
    template = "clientapp/contactus.html"
    context = {'contact_form': contact_form, 'errors': errors}
    return render(request, template, context)


def adminReport(request):
    individual_messages = Delivery_Status.objects.all()
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
    if (command == 'login'):
        if not weblayer.assertConnected():
            weblayer.login('918200594756', 'Db1rSq/g8EzVgs+LbWp2idQcUUc=')

    elif (command == 'connection_status'):
        return HttpResponse(weblayer.assertConnected())

    elif (command == 'send'):
        id = request.GET.get('id', '')
        if len(id) < 1:
            return HttpResponse(False)
        msg_object = Delivery_Status.objects.filter(id=id, delivery_status=0)
        if (len(msg_object) > 0):
            msg_object = msg_object[0]
            weblayer.send_message(msg_object)
            return HttpResponse(True)

    elif (command == 'status'):
        id = request.GET.get('id', '')
        if len(id) < 1:
            return HttpResponse(False)
        msg_object = Delivery_Status.objects.filter(id=id)
        if (len(msg_object) > 0) and (msg_object[0].delivery_status == 1):
            return HttpResponse(True)
    
    elif (command == 'video'):
        mobilenumber = '919428919278'
        path = "/home/alex/Desktop/ezgif-2-f229160e22.mp4"
        weblayer.media_send(mobilenumber, path, "video" , None)
        return HttpResponse(True)

    # Default Case if nothing else works
    return HttpResponse(False)


def api_mainpage(request, id=None):
    if id is None:
        msg_formats = [i for i in Whatsapp_Message_Format.objects.filter(user__is_active=True) if i.unsent_msg() > 0]
        template = "clientapp/whatsapp_mainpage.html"
        context = {'msg_formats': msg_formats}
        return render(request, template, context)
    else:
        obj = Delivery_Status.objects.filter(message_format__id=id, delivery_status=0)
        if len(obj)>0:
            message_format = obj[0].message_format
        else:
            message_format = None

        contacts = [status.to_number.number for status in obj]
        weblayer.contacts_sync(contacts)
        template = "clientapp/whatsapp_message.html"
        context = {'message_format':message_format,  'messages' : obj}
        return render(request, template, context)