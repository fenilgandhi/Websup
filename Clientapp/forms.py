from django import forms
import Clientapp.models as models


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.MyUser
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
        model = models.MyUser
        readonly_fields = ("created_on", "is_admin")
        fields = ('name', 'email', 'password', 'total_credits', 'remaining_credits', 'used_credits', 'queued_credits')


    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class Contactus_Form(forms.ModelForm):
    class Meta:
        model = models.Contactus
        exclude = ("",)


class Whatsapp_Text_Form(forms.ModelForm):
    class Meta:
        model = models.Whatsapp_Text
        exclude = ("format",)
        widgets = {
            'text' : forms.Textarea(attrs={ 'class':'form-control'}),
        }


class Whatsapp_Image_Form(forms.ModelForm):
    class Meta:
        model = models.Whatsapp_Image
        exclude = ("format",)
        label= { 'image' : forms.ClearableFileInput(attrs={'class' : 'control-label'}),
        }
        widgets = {
            'image' : forms.FileInput(attrs={ 'class':'filestyle' }),
        }

class Whatsapp_vCard_Form(forms.ModelForm):
    class Meta:
        model = models.Whatsapp_vCard
        exclude = ("format",)
        widgets = {
            'name'        : forms.TextInput(attrs={ 'class':'form-control' }),
            'person_name' : forms.TextInput(attrs={ 'class':' form-control' }),
            'company'     : forms.TextInput(attrs={ 'class':' form-control' }),
            'mobile1'     : forms.TextInput(attrs={ 'class':' form-control' }),
            'mobile2'     : forms.TextInput(attrs={ 'class':' form-control' }),
            'mobile3'     : forms.TextInput(attrs={ 'class':' form-control' }),
            'address'     : forms.TextInput(attrs={ 'class':' form-control' }),
            'email'       : forms.EmailInput(attrs={ 'class':' form-control' }),
            'url'         : forms.URLInput(attrs={ 'class':' form-control' }),
        }

class Whatsapp_New_Message_Form(forms.ModelForm):
    class Meta:
        model = models.Whatsapp_Message_Format
        exclude = ('user', 'added_on')
