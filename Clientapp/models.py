from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


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
            model = MyUser
            exclude = ("",)


class MyUser(AbstractBaseUser):
    name = models.CharField(verbose_name='Full Name', max_length=255, unique=False, null=False, blank=False)
    email = models.EmailField(verbose_name='Email Address', max_length=255, unique=True, null=False, blank=False)
    # password is AutoField from AbstractBaseUser
    created_on = models.DateTimeField(verbose_name="Account Created on ", auto_now=False, auto_now_add=True)

    total_credits = models.IntegerField(verbose_name="Total Credits", default=0)
    remaining_credits = models.IntegerField(verbose_name="Remaining Credits", default=0)
    used_credits = models.IntegerField(verbose_name="Used Credits", default=0)
    queued_credits = models.IntegerField(verbose_name="Queued Credits", default=0)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_active

    def update_credits(self):
        # Update Total Credits
        user_plans = User_Plan.objects.filter(user__id=self.id)
        if len(user_plans) > 0:
            self.total_credits = sum([user_plan.plan.credits for user_plan in user_plans])
        else:
            self.total_credits = 0

        # Update Queued Credits
        queued_messages = Delivery_Status.objects.filter(message_format__user=self, delivery_status=0).count()
        self.queued_credits = queued_messages

        # Update Sent Credits
        sent_messages = Delivery_Status.objects.filter(message_format__user=self, delivery_status=1).count()
        self.used_credits = sent_messages

        # Update Remaining Credits
        self.remaining_credits = self.total_credits - self.queued_credits - self.used_credits
        self.save()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'Website User'


class Whatsapp_Plan(models.Model):
    name_of_plan = models.CharField(verbose_name="Plan name", max_length=50, null=False, blank=False)
    price = models.IntegerField(verbose_name="Amount Paid")
    credits = models.IntegerField(verbose_name="Offered Credits")
    description = models.TextField(verbose_name='Description', blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name_of_plan

    class Meta:
        verbose_name_plural = 'Whatsapp Plan'


class User_Plan(models.Model):
    user = models.ForeignKey(MyUser)
    plan = models.ForeignKey(Whatsapp_Plan)
    paid_amount = models.IntegerField(verbose_name='Paid Amount', default=0)
    started_on = models.DateField(verbose_name="Subscribed On", auto_now=False, auto_now_add=True)

    objects = MyUserManager()

    def save(self, *args, **kwargs):
        super(User_Plan, self).save(*args, **kwargs)
        self.user.update_credits()

    def __str__(self):
        return "-".join([self.user.email, self.plan.name_of_plan])

    class Meta:
        verbose_name_plural = 'User Plan'


class Whatsapp_Credentials(models.Model):
    number = models.CharField(verbose_name='Mobile Number', max_length=12, blank=False, null=False, unique=True)
    password = models.CharField(verbose_name='Password', max_length=70, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Yowsup Credentials'


class Whatsapp_Number(models.Model):
    number = models.CharField(verbose_name='Mobile Number', max_length=12, blank=False, null=False, unique=True)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name_plural = 'Whatsapp Contact Number'


class Contactus(models.Model):
    name = models.CharField(verbose_name="name", max_length=25, null=False, blank=False)
    contact_number = models.IntegerField(verbose_name="Mobile Number")
    email_address = models.EmailField(verbose_name="Email Address", max_length=255, unique=True, null=False, blank=False)
    text_message = models.CharField(verbose_name="Problem Description", max_length=1500, null=True, blank=False)
    added_on = models.DateTimeField(verbose_name="Added On", auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Contact Us'

    def __str__(self):
        return "-".join([self.name, str(self.added_on)])


class Whatsapp_Message_Format(models.Model):
    format_name = models.CharField(verbose_name="Advertisement Name", max_length=100, null=False, blank=True)
    user = models.ForeignKey(MyUser)
    added_on = models.DateTimeField(verbose_name='Added On', auto_now=False, auto_now_add=True)
    mobile_numbers = models.ManyToManyField(Whatsapp_Number)

    def unsent_msg(self):
        a = Text_Delivery.objects.filter(message_text__format=self, delivery_status=0).count()
        b = Image_Delivery.objects.filter(message_image__format=self, delivery_status=0).count()
        c = vCard_Delivery.objects.filter(message__format=self, delivery_status=0).count()
        return a+b+c
        

    def __str__(self):
        return "-".join([self.user.name, self.format_name])

    class Meta:
        verbose_name_plural = 'Whatsapp Message Formats'


class Whatsapp_vCard(models.Model):
    format = models.ForeignKey(Whatsapp_Message_Format)
    name = models.CharField(verbose_name="vCard Name", max_length=50, blank=False, null=False)
    person_name = models.CharField(verbose_name="Person Name", max_length=150, blank=False, null=False)
    company = models.CharField(verbose_name="Company", max_length=200, blank=True)
    mobile1 = models.CharField(verbose_name="Mobile Number 1", max_length=15, blank=True)
    mobile2 = models.CharField(verbose_name="Mobile Number 2", max_length=15, blank=True)
    mobile3 = models.CharField(verbose_name="Mobile Number 3", max_length=15, blank=True)
    address = models.CharField(verbose_name="Address", max_length=300, blank=True)
    email = models.EmailField(verbose_name="Email", max_length=50, blank=True)
    url = models.URLField(verbose_name="Website", blank=True)

    class Meta:
        verbose_name_plural = 'Whatsapp vCard'


class Whatsapp_Image(models.Model):
    format = models.ForeignKey(Whatsapp_Message_Format)
    image = models.ImageField(upload_to='img', null=True, blank=True)

    def __str__(self):
            return "{0}".format(self.image.url)

    class Meta:
        verbose_name_plural = 'Whatsapp Image'


class Whatsapp_Text(models.Model):
    format = models.ForeignKey(Whatsapp_Message_Format)
    text = models.CharField(verbose_name='Text Content', max_length=1500, blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.text)

    class Meta:
        verbose_name_plural = 'Whatsapp Text'


class Delivery_Status(models.Model):
    to_number = models.ForeignKey(Whatsapp_Number, related_name='to_whatsapp_number')
    message_format = models.ForeignKey(Whatsapp_Message_Format)
    added_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    whatsapp_message_id = models.CharField(verbose_name="Whatsapp generated id", max_length=50, blank=True, null=True)
    delivery_status = models.IntegerField(default=0)
    delivery_time = models.DateTimeField(verbose_name="Delivery Time", auto_now=False, auto_now_add=True, blank=True, null=True)
    sent_using = models.ForeignKey(Whatsapp_Credentials, related_name='sent_using', blank=True, null=True)

    def __str__(self):
        return "{0}-{1}".format( self.to_number.number, self.delivery_status)

    class Meta:
        verbose_name_plural = 'Delivery Status'


class Text_Delivery(Delivery_Status):
    message_text = models.ForeignKey(Whatsapp_Text)

    class Meta:
        verbose_name_plural = 'Delivery Text'


class Image_Delivery(Delivery_Status):
    message_image = models.ForeignKey(Whatsapp_Image)

    class Meta:
        verbose_name_plural = 'Delivery Image'


class vCard_Delivery(Delivery_Status):
    message = models.ForeignKey(Whatsapp_vCard)

    class Meta:
        verbose_name_plural = 'Delivery vCard'
