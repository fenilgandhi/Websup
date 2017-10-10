from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import *

from functools import update_wrapper
from django.http import Http404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


def admin_view(view, cacheable=False):
    """
    Overwrite the default admin view to return 404 for not logged in users.
    """
    def inner(request, *args, **kwargs):
        if not (request.user.is_active and request.user.is_admin):
            raise Http404()
        return view(request, *args, **kwargs)

    if not cacheable:
        inner = never_cache(inner)

    # We add csrf_protect here so this function can be used as a utility
    # function for any view, without having to repeat 'csrf_protect'.
    if not getattr(view, 'csrf_exempt', False):
        inner = csrf_protect(inner)

    return update_wrapper(inner, view)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        readonly_fields = ("created_on", "is_admin")
        fields = ('name', 'email', 'password')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    # password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        readonly_fields = ("created_on", "is_admin")
        fields = ('name', 'email', 'password', 'total_credits', 'remaining_credits', 'used_credits', 'queued_credits')
    
    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    readonly_fields = ("created_on", "is_admin")
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_active', 'is_admin')
    list_filter = ('is_admin', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'password', 'total_credits', 'remaining_credits', 'used_credits', 'queued_credits', "is_admin", "created_on")
        }),
        ('Permissions', {
            'fields': ('is_active',)
        }),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'fields': ('name', 'email', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active',)
        }),
    )
    search_fields = ('email',)
    ordering = ('email', 'is_active')
    filter_horizontal = ()


class Whatsapp_Plans_Admin(admin.ModelAdmin):
    model = Whatsapp_Plans
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("name_of_plan", "price", "credits", "description", "is_active")}
         ),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("name_of_plan", "price", "credits", "description", "is_active")}
         ),
    )
    list_display = ("name_of_plan", "price", "credits", "is_active")


class User_Plan_Admin(admin.ModelAdmin):
    model = User_Plan
    list_display = ("user", "plan", "started_on", "paid_amount")


class Whatsapp_Number_Admin(admin.ModelAdmin):
    model = Whatsapp_Number
    list_display = ("number",)


class Whatsapp_Message_Format_Admin(admin.ModelAdmin):
    model = Whatsapp_Message_Format
    list_display = ("format_name", "user", "added_on")


class ContactUs_Admin(admin.ModelAdmin):
    model = ContactUs
    list_display = ("name", "contact_number", "email_address", "text_message")


admin.site.unregister(Group)
# admin.site.register(Whatsapp_Plans, Whatsapp_Plans_Admin)
# admin.site.register(User_Plan, User_Plan_Admin)
# admin.site.register(Whatsapp_Number, Whatsapp_Number_Admin)
# admin.site.register(Whatsapp_Message_Format, Whatsapp_Message_Format_Admin)
# admin.site.register(Whatsapp_Individual_Message, Whatsapp_Individual_Message_Admin)
# admin.site.register(ContactUs, ContactUs_Admin)


admin.site.register(MyUser, UserAdmin)
admin.site.register(User_Plan, User_Plan_Admin)
admin.site.register(Whatsapp_Plans)
admin.site.register(ContactUs, ContactUs_Admin)

admin.site.register(Whatsapp_Number)
admin.site.register(Whatsapp_Image)
admin.site.register(Whatsapp_Text)
admin.site.register(Whatsapp_vCard)

admin.site.register(Whatsapp_Credentials)

admin.site.register(Text_Delivery)
admin.site.register(Image_Delivery)
admin.site.register(vCard_Delivery)
admin.site.register(Whatsapp_Message_Format)
