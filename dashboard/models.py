from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.forms import ModelForm , TextInput , Select  , FileInput , ChoiceField
from django.utils.translation import ugettext_lazy as _


class MyUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Plan(models.Model):
	name_of_plan = models.CharField(verbose_name = "Plan name", max_length=50, null=False, blank=False)
	credits = models.IntegerField(verbose_name = "Credits")
	price = models.IntegerField(verbose_name = "Price")
	duration = models.CharField(verbose_name = "Validity", max_length=30, null=False, blank=False)
	description = models.TextField(verbose_name='Description', blank=True)

	def __str__(self):
		return "-".join([self.name_of_plan , str(self.credits) , str(self.price), str(self.duration)])


class User_Plan(models.Model):
	user = models.ForeignKey(MyUser)
	plan = models.ForeignKey(Plan)
	started_on = models.DateField(_("Subscribed On"), auto_now=False , auto_now_add=True)
	paid_amount = models.IntegerField(verbose_name='Paid Amount', default=0)
	total_credits = models.IntegerField(verbose_name='Total Credits')
	used_credits = models.IntegerField(verbose_name='Used Credits')
	remaining_credits = models.IntegerField(verbose_name='Remaining Credits')
	ending_on = models.DateField(_("Valid Upto"), auto_now=False , auto_now_add=True)
	

class Contact(models.Model):
	number = models.IntegerField(verbose_name='Mobile Number' , max_length=20, blank=False, null=False)


class WhatApp_Message_Format(models.Model):
	from_user = models.ForeignKey(MyUser)
	sent_on = models.DateField(_("Sent On"), auto_now=False , auto_now_add=True)
	msg_text = models.CharField(verbose_name='message' , max_length=1500, blank=True, null=True)
	## To implement after django-media setup
	# msg_img1
	# msg_img2
	# msg_img3
	# msg_img4
	# msg_doc

	
class WhatsApp_Bulk_Message(models.Model):
	to_contact = models.ForeignKey(Contact)
	message_format = models.ForeignKey(WhatApp_Message_Format)
	delivered = models.BooleanField(default=False)
