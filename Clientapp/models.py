from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.forms import ModelForm
from django.core.urlresolvers import reverse

# Custom User Manager


class MyUserManager(BaseUserManager):

    def create_user(self, name, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not name:
            raise ValueError('User must have a Name')

        user = self.model(email=self.normalize_email(email))

        user.name = name
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password):
        user = self.create_user(name, email, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

        class Meta:
            model = Person
            exclude = ("",)

class MyUser(AbstractBaseUser):
    name = models.CharField(verbose_name='Name', max_length=255, unique=False, null=False, blank=False)
    email = models.EmailField(verbose_name='Email Address', max_length=255, unique=True, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    total_credits = models.IntegerField(verbose_name="Total Credits", default=0)
    remaining_credits = models.IntegerField(verbose_name="Remaining Credits", default=0)
    used_credits = models.IntegerField(verbose_name="Used Credits", default=0)

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

    def update_credits(self):
        plans = User_Plan.objects.filter(user=self)
        total_credits = 0
        remaining_credits = 0
        used_credits = 0
        for plan in plans:
            total_credits += plan.total_credits
            remaining_credits += plan.remaining_credits
            used_credits += plan.used_credits
        self.total_credits = total_credits
        self.remaining_credits = remaining_credits
        self.used_credits = used_credits
        self.save()

    @property
    def is_staff(self):
        # Is the user a member of staff?
        return self.is_active

class contactus(models.Model):
    name = models.CharField(verbose_name="name", max_length=25, null=False, blank=False)
    contact_number = models.IntegerField(verbose_name="Mobile Number")
    email_address = models.EmailField(verbose_name="Email Address", max_length=255, unique=True, null=False, blank=False)
    contact_msg = models.CharField(verbose_name="Contact message", max_length=1500, null=True, blank=False)

    class Meta:
        verbose_name_plural = 'Contact Us'

    def __str__(self):
        return "-".join([self.name, str(self.contact_number)])

class Plan(models.Model):
    is_active = models.BooleanField(default=False)
    name_of_plan = models.CharField(verbose_name="Plan name", max_length=50, null=False, blank=False)
    credits = models.IntegerField(verbose_name="Credits")
    price = models.IntegerField(verbose_name="Price")
    duration = models.CharField(verbose_name="Validity", max_length=30, null=False, blank=False)
    description = models.TextField(verbose_name='Description', blank=True)

    def __str__(self):
        return self.name_of_plan

class User_Plan(models.Model):
    objects = MyUserManager()
    user = models.ForeignKey(MyUser)
    plan = models.ForeignKey(Plan)
    started_on = models.DateField(verbose_name="Subscribed On", auto_now=False, auto_now_add=True)
    paid_amount = models.IntegerField(verbose_name='Paid Amount', default=0)
    total_credits = models.IntegerField(verbose_name='Total Credits')
    used_credits = models.IntegerField(verbose_name='Used Credits')
    remaining_credits = models.IntegerField(verbose_name='Remaining Credits')
    ending_on = models.DateField(verbose_name="Valid Upto", auto_now=False, auto_now_add=True)

    def update_credits(self):
        self.total_credits = self.plan.credits
        self.used_credits = 0
        self.remaining_credits = self.total_credits
    
    def save(self, *args, **kwargs):
        super(User_Plan, self).save(*args, **kwargs)
        self.user.update_credits()

    def delete(self, *args, **kwargs):
        super(User_Plan, self).delete(*args, **kwargs)
        self.user.update_credits()

    def __str__(self):
        return "-".join([self.user.email, self.plan.name_of_plan])

class Contact(models.Model):
    number = models.CharField(verbose_name='Mobile Number', max_length=20, blank=False, null=False, unique=True)

    def __str__(self):
        return self.number

class WhatApp_Message_Format(models.Model):
    campaign_name = models.CharField(max_length=100, null=False, blank=True)
    from_user = models.ForeignKey(MyUser, null=True)
    sent_on = models.DateField(verbose_name='Sent On', auto_now=False, auto_now_add=True)
    msg_text = models.CharField(verbose_name='message', max_length=1500, blank=True, null=True)

    # To implement after django-media setup
    msg_img1 = models.FileField(null=True, blank=True)
    msg_img2 = models.FileField(null=True, blank=True)
    # msg_img3
    # msg_img4
    # msg_doc

    def __str__(self):
        return "-".join([self.from_user.name, self.campaign_name])


class WhatsApp_Individual_Message(models.Model):
    to_contact = models.ForeignKey(Contact, related_name='to_contact')
    message_format = models.ForeignKey(WhatApp_Message_Format)
    delivered = models.BooleanField(default=False)
    sent_using = models.ForeignKey(Contact, related_name='sent_using' , blank=True, null=True)
    sent_on = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)

#################################################################################################
#									Model Form													#
#################################################################################################


class Whatsapp_Message_Form(ModelForm):

    class Meta:
        model = WhatApp_Message_Format
        exclude = ('from_user',)


class Whatsapp_indvidual_message_form(ModelForm):

    class Meta:
        model = WhatsApp_Individual_Message
        exclude = ("",)


class ContactusForm(ModelForm):

    class Meta:
        model = contactus
        exclude = ("",)
