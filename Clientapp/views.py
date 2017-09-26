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

from Clientapp.forms import PasswordRecoveryForm, PasswordResetForm
from Clientapp.signals import user_recovers_password

# from .yowsup_integration.stack import *

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


#####################
#   Password reset
#####################
class SaltMixin(object):
	salt = 'password_recovery'
	url_salt = 'password_recovery_url'


def loads_with_timestamp(value, salt):
	"""Returns the unsigned value along with its timestamp, the time when it
	got dumped."""
	try:
		signing.loads(value, salt=salt, max_age=-999999)
	except signing.SignatureExpired as e:
		age = float(str(e).split('Signature age ')[1].split(' >')[0])
		timestamp = timezone.now() - datetime.timedelta(seconds=age)
		return timestamp, signing.loads(value, salt=salt)


class RecoverDone(SaltMixin, generic.TemplateView):
	template_name = 'password_reset/reset_sent.html'

	def get_context_data(self, **kwargs):
		ctx = super(RecoverDone, self).get_context_data(**kwargs)
		try:
			ctx['timestamp'], ctx['email'] = loads_with_timestamp(
				self.kwargs['signature'], salt=self.url_salt,
			)
		except signing.BadSignature:
			raise Http404
		return ctx


recover_done = RecoverDone.as_view()


class Recover(SaltMixin, generic.FormView):
	case_sensitive = True
	form_class = PasswordRecoveryForm
	template_name = 'password_reset/recovery_form.html'
	success_url_name = 'password_reset_sent'
	email_template_name = 'password_reset/recovery_email.txt'
	email_subject_template_name = 'password_reset/recovery_email_subject.txt'
	search_fields = ['username', 'email']

	def get_success_url(self):
		return reverse(self.success_url_name, args=[self.mail_signature])

	def get_context_data(self, **kwargs):
		kwargs['url'] = self.request.get_full_path()
		return super(Recover, self).get_context_data(**kwargs)

	def get_form_kwargs(self):
		kwargs = super(Recover, self).get_form_kwargs()
		kwargs.update({
			'case_sensitive': self.case_sensitive,
			'search_fields': self.search_fields,
		})
		return kwargs

	def get_site(self):
		return get_current_site(self.request)

	def send_notification(self):
		context = {
			'site': self.get_site(),
			'user': self.user,
			'username': self.user.get_username(),
			'token': signing.dumps(self.user.pk, salt=self.salt),
			'secure': self.request.is_secure(),
		}
		body = loader.render_to_string(self.email_template_name,
									   context).strip()
		subject = loader.render_to_string(self.email_subject_template_name,
										  context).strip()
		send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
				  [self.user.email])

	def form_valid(self, form):
		self.user = form.cleaned_data['user']
		self.send_notification()
		if (
			len(self.search_fields) == 1 and
			self.search_fields[0] == 'username'
		):
			# if we only search by username, don't disclose the user email
			# since it may now be public information.
			email = self.user.username
		else:
			email = self.user.email
		self.mail_signature = signing.dumps(email, salt=self.url_salt)
		return super(Recover, self).form_valid(form)


recover = Recover.as_view()


class Reset(SaltMixin, generic.FormView):
	form_class = PasswordResetForm
	token_expires = None
	template_name = 'password_reset/reset.html'
	success_url = reverse_lazy('password_reset_done')

	def get_token_expires(self):
		duration = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRES',
						   self.token_expires)
		if duration is None:
			duration = 3600 * 48  # Two days
		return duration

	@method_decorator(sensitive_post_parameters('password1', 'password2'))
	def dispatch(self, request, *args, **kwargs):
		self.request = request
		self.args = args
		self.kwargs = kwargs
		self.user = None

		try:
			pk = signing.loads(kwargs['token'],
							   max_age=self.get_token_expires(),
							   salt=self.salt)
		except signing.BadSignature:
			return self.invalid()

		self.user = get_object_or_404(get_user_model(), pk=pk)
		return super(Reset, self).dispatch(request, *args, **kwargs)

	def invalid(self):
		return self.render_to_response(self.get_context_data(invalid=True))

	def get_form_kwargs(self):
		kwargs = super(Reset, self).get_form_kwargs()
		kwargs['user'] = self.user
		return kwargs

	def get_context_data(self, **kwargs):
		ctx = super(Reset, self).get_context_data(**kwargs)
		if 'invalid' not in ctx:
			ctx.update({
				'username': self.user.get_username(),
				'token': self.kwargs['token'],
			})
		return ctx

	def form_valid(self, form):
		form.save()
		user_recovers_password.send(
			sender=get_user_model(),
			user=form.user,
			request=self.request
		)
		return redirect(self.get_success_url())


reset = Reset.as_view()


class ResetDone(generic.TemplateView):
	template_name = 'password_reset/recovery_done.html'


reset_done = ResetDone.as_view()
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
			return HttpResponse("Connected")
		else:
			return HttpResponse("Disconnected")

	if command == 'send':
		for token in 'If you are reading this message, then the demo is live.'.split(' '):
			weblayer.message_send('919999999999' , token)
		return None

def api_gui(request):
	msg_formats = WhatsApp_Individual_Message.objects.filter(delivered=False, message_format__is_approved=True, message_format__from_user__is_active=True)
	template = "clientapp/whatsapp.html"
	context = { 'msg_formats' : msg_formats }
	return render(request, template, context)