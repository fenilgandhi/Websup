from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom User Manager
class MyUserManager(BaseUserManager):
	def create_user(self, name, email, password=None):
		if not email:  raise ValueError('User must have an email address')
		if not name: raise ValueError('User must have a Name')

		user = self.model( email=self.normalize_email(email) )

		user.name = name
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, name, email,  password):
		user = self.create_user( name, email, password=password)
		user.is_admin = True
		user.save(using=self._db)
		return user
	
class MyUser(AbstractBaseUser):
	name = models.CharField( verbose_name='Name', max_length=255, unique=False, null=False, blank=False )
	email = models.EmailField( verbose_name='Email Address', max_length=255, unique=True, null=False, blank=False )
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = MyUserManager()

	USERNAME_FIELD = 'email'

	def get_full_name(self):
		return self.name

	def get_short_name(self):
		return self.name

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		# Is the user a member of staff?
		return self.is_admin

class Plan(models.Model):
	is_active = models.BooleanField(default=False)
	name_of_plan = models.CharField(verbose_name="Plan name", max_length=50, null=False, blank=False)
	credits = models.IntegerField(verbose_name="Credits")
	price = models.IntegerField(verbose_name="Price")
	duration = models.CharField(verbose_name="Validity", max_length=30, null=False, blank=False)
	description = models.TextField(verbose_name='Description', blank=True)

	def __str__(self):
		return "-".join([self.name_of_plan, str(self.credits), str(self.price), str(self.duration)])

class User_Plan(models.Model):
	user = models.ForeignKey(MyUser)
	plan = models.ForeignKey(Plan)
	started_on = models.DateField( verbose_name = "Subscribed On", auto_now=False, auto_now_add=True)
	paid_amount = models.IntegerField(verbose_name='Paid Amount', default=0)
	total_credits = models.IntegerField(verbose_name='Total Credits')
	used_credits = models.IntegerField(verbose_name='Used Credits')
	remaining_credits = models.IntegerField(verbose_name='Remaining Credits')
	ending_on = models.DateField(verbose_name = "Valid Upto", auto_now=False, auto_now_add=True)

	def __str__(self):
		return "-".join([self.user, self.plan])

class Contact(models.Model):
	number = models.CharField(verbose_name='Mobile Number', max_length=20, blank=False, null=False, unique=True)

	def __str__(self):
		return self.number

class WhatApp_Message_Format(models.Model):
	campaign_name = models.CharField(max_length=100, null=False, blank=True)
	from_user = models.ForeignKey(MyUser)
	sent_on = models.DateField(verbose_name='Sent On', auto_now=False, auto_now_add=True)
	msg_text = models.CharField(verbose_name='message', max_length=1500, blank=True, null=True)
	# To implement after django-media setup
	# msg_img1
	# msg_img2
	# msg_img3
	# msg_img4
	# msg_doc

	def __str__(self):
		return "-".join([self.from_user.name, self.campaign_name])

class WhatsApp_Individual_Message(models.Model):
	to_contact = models.ForeignKey(Contact , related_name='to_contact')
	message_format = models.ForeignKey(WhatApp_Message_Format)
	delivered = models.BooleanField(default=False)
	sent_using = models.ForeignKey(Contact , related_name='sent_using')
	sent_on = models.DateTimeField(auto_now=False, auto_now_add=False)
