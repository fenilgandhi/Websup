from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import *
from .forms import *

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
            'fields': ('name', 'email', 'password1', 'password2')
        }),
        ('Permissions', {
            'fields': ('is_active',)
        }),
    )
    search_fields = ('email',)
    ordering = ('email', 'is_active')
    filter_horizontal = ()


class Whatsapp_Plan_Admin(admin.ModelAdmin):
    model = Whatsapp_Plan
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


class Contactus_Admin(admin.ModelAdmin):
    model = Contactus
    list_display = ("name", "contact_number", "email_address", "text_message")


class Whatsapp_Number_Admin(admin.ModelAdmin):
    model = Whatsapp_Number
    list_display = ("number",)


class Whatsapp_Credentials_Admin(admin.ModelAdmin):
    model = Whatsapp_Credentials


class Whatsapp_Text_Admin(admin.ModelAdmin):
    model = Whatsapp_Text


class Whatsapp_Image_Admin(admin.ModelAdmin):
    model = Whatsapp_Image


class Whatsapp_Image_Inline(admin.TabularInline):
    model = Whatsapp_Image
    extra = 1

class Whatsapp_Text_Inline(admin.TabularInline):
    model = Whatsapp_Text
    extra = 1

class Whatsapp_vCard_Inline(admin.TabularInline):
    model = Whatsapp_vCard
    extra = 1


class Whatsapp_vCard_Admin(admin.ModelAdmin):
    model = Whatsapp_vCard


class Text_Delivery_Admin(admin.ModelAdmin):
    model = Text_Delivery
    list_display = ("id" , "to_number")


class Image_Delivery_Admin(admin.ModelAdmin):
    model = Image_Delivery
    list_display = ("id" , "to_number")


class vCard_Delivery_Admin(admin.ModelAdmin):
    model = vCard_Delivery
    list_display = ("id" , "to_number")


class Whatsapp_Message_Format_Admin(admin.ModelAdmin):
    model = Whatsapp_Message_Format
    #readonly_fields = "mobile_numbers",
    list_display = ("format_name", "user", "added_on")
    inlines = (Whatsapp_Text_Inline, Whatsapp_Image_Inline, Whatsapp_vCard_Inline)


admin.site.admin_view = admin_view
admin.site.unregister(Group)
admin.site.register(MyUser, UserAdmin)
admin.site.register(Whatsapp_Plan)
admin.site.register(User_Plan, User_Plan_Admin)

admin.site.register(Contactus, Contactus_Admin)

admin.site.register(Whatsapp_Credentials, Whatsapp_Credentials_Admin)
admin.site.register(Whatsapp_Number, Whatsapp_Number_Admin)
admin.site.register(Whatsapp_Image, Whatsapp_Image_Admin)
admin.site.register(Whatsapp_Text, Whatsapp_Text_Admin)
admin.site.register(Whatsapp_vCard, Whatsapp_vCard_Admin)

admin.site.register(Text_Delivery, Text_Delivery_Admin)
admin.site.register(Image_Delivery, Image_Delivery_Admin)
admin.site.register(vCard_Delivery, vCard_Delivery_Admin)
admin.site.register(Whatsapp_Message_Format, Whatsapp_Message_Format_Admin)