from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.

def index(request):
    return render(request, "index.html")

def bulk_whatsapp(request):
	return render(request, "Bulk_whatsapp.html")

# def register(request):
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             new_user_name = form.cleaned_data['username']
#             new_user_password = form.cleaned_data['password1']
#             new_user_email = form.cleaned_data['email']
#             new_user = User.objects.create_user(username=new_user_name,
#                                                 email=new_user_email,
#                                                 password=new_user_password)
#             new_user.is_active = False
#             new_user.save()
#             new_user_token = activation_user().make_token(new_user)
#             host = request.get_host()

#             send_mail("Activate YOur Account",
#                       loader.render_to_string('user_activate.html',
#                                               {'pk': new_user.id,
#                                                'token': new_user_token,
#                                                'domain': host,
#                                                'user': new_user_name}), 'test.gahan@gmail.com', ['gahan@quixom.com', new_user_email])
#             return HttpResponseRedirect('/login/')
#     else:
#         form = SignUpForm()
#     return render(request, 'registration.html', {'form': form})


# def activate_new_user(request, pk, token):
#     usr = User.objects.get(pk=pk)
#     verified = activation_user().check_token(usr, token)
#     if verified:
#         usr.is_active = True
#         usr.save()
#         return HttpResponseRedirect('/')
#     else:
#         return HttpResponse("Invalid Verification Link")