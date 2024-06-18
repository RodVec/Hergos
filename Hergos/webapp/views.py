from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login
from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegisterForm, CustomUserChangeForm
from .models import User

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.conf import settings
from datetime import timedelta

from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from django.core.mail import EmailMessage
from smtplib import SMTPServerDisconnected

def home(request):
    return render(request, "home.html")

def policy(request):
    return render(request, "policy/policy.html")


@login_required
def user_view(request):
    user_name = request.session.get('user_name', '')
    last_name = request.session.get('last_name', '')
    return render(request, "users/user_view.html", {'user_name': user_name, 'last_name': last_name})




@login_required
def comofunciona(request):
    return render(request, 'users/comofunciona.html')

@login_required
def ayuda(request):
    return render(request, 'ayuda.html')













@login_required
def user_profile(request):
    return render(request, 'users/user_profile.html')



@login_required
def configuracion(request):
    return render(request, 'users/configuracion/configuracion.html')

from django.shortcuts import render, get_object_or_404
@login_required
def user_login_delete(request, user_email):

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user_email == user.email:
                    messages.error(request, ("Erro de autenticación"))
                    return render(request, 'users/configuracion/login_delete.html', {'form': form})
                
                else:
                    # mail de confirmación
                    current_site = get_current_site(request)  
                    mail_subject = 'Elimiación de cuenta Hergos'

                    message = render_to_string('users/mail/delete.html', {  
                        'user': user,  
                        'domain': current_site.domain,
                    })  
                    to_email = form.cleaned_data.get('email')  
                    email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
                    )  
                    email.send()  

                    user.delete()

                    return redirect("home")
            else:
                messages.error(request, ("Email o contraseña incorrectos"))
                return render(request, 'users/configuracion/login_delete.html', {'form': form})
    else:
        form = UserLoginForm()

    return render(request, 'users/configuracion/login_delete.html', {'form': form})

@login_required
def editar(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, ("Cambios guardados correctamente"))
            return redirect('configuracion')
    
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/editar.html', {'form': form})


def user_login_editar(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            #hashed_password = make_password(password)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if not user.email_is_verified:
                    messages.error(request, ("Tu mail no ha sido verificado"))
                    return render(request, 'users/configuracion/login_editar.html', {'form': form})
                
                else:
                    login(request, user)

                    # Almacena el nombre del usuario en la sesión
                    request.session['user_name'] = user.name
                    request.session['last_name'] = user.last_name

                    return redirect("editar")
            else:
                print(user)
                # El usuario no pudo ser autenticado, puedes manejar esto como desees
                messages.error(request, ("email o contraseña incorrectos"))
                return render(request, 'users/configuracion/login_editar.html', {'form': form})
    else:
        form = UserLoginForm()

    return render(request, 'users/configuracion/login_editar.html', {'form': form})
























# Signal handler for user_logged_in
@receiver(user_logged_in)
def update_last_login(sender, request, user, **kwargs):
    # Update last_login field to the current datetime when the user logs in
    user.last_login = timezone.now()
    user.save()

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            #hashed_password = make_password(password)
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if not user.email_is_verified:
                    messages.error(request, ("Tu mail no ha sido verificado"))
                    return render(request, 'users/login.html', {'form': form})
                
                else:
                    login(request, user)

                    # Almacena el nombre del usuario en la sesión
                    request.session['user_name'] = user.name
                    request.session['last_name'] = user.last_name

                    return redirect("user_view")
            else:
                print(user)
                # El usuario no pudo ser autenticado, puedes manejar esto como desees
                messages.error(request, ("email o contraseña incorrectos"))
                return render(request, 'users/login.html', {'form': form})
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})



def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_is_verified = False
            user.username = user.email
            user.save()

            current_site = get_current_site(request)  
            mail_subject = 'Activación de cuenta Hergos'

            expiration_minutes = settings.ACCOUNT_ACTIVATION_MINUTES
            expiration_date = timezone.now() + timedelta(minutes=expiration_minutes)

            message = render_to_string('verify_email/verify_email_message.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user), 
                'expiration_date': expiration_date,
            })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                mail_subject, message, to=[to_email]  
            )  
            email.send()  
            messages.success(request,"Revisa tu mail para completar el registro") 
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, 'users/signup.html', {'form': form})




def verify_email_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_is_verified = True
        user.save()
        messages.success(request, 'Tu mail ha sido verificado')

        message = render_to_string('users/mail/welcome.html', {  
            'user': user,
        })  
        to_email = user.email  
        mail_subject = 'Bienvenido a AsesorBot'  
        email = EmailMessage(  
            mail_subject, message, to=[to_email]  
        ) 
        email.send()

        return redirect('login')
    else:
        messages.warning(request, 'Este link ya no es válido')
        return render(request, 'verify_email/verify_email_confirm.html')

from django.contrib.auth import logout
def user_logout(request):
    logout(request)
    return redirect("home")  












def contact_form_view(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            if not name or not email or not subject or not message:
                messages.error(request, "Por favor, completa todos los campos")
                return redirect(request.META.get('HTTP_REFERER', 'http://127.0.0.1:443') + ("#contact"))


            # Procesa los datos como desees, por ejemplo, enviando un correo electrónico
            email = EmailMessage(
                subject,
                f'Mensaje de: {name}\nCorreo electrónico: {email}\n\n{message}',
                settings.EMAIL_HOST_USER,
                ['hergos.soporte@gmail.com'], # destino
            )

            email.send()

            messages.success(request, ("Mensaje enviado, contactaremos con usted lo antes posible"))
            return redirect(request.META.get('HTTP_REFERER', 'http://127.0.0.1:443') + ("#contact"))
    except SMTPServerDisconnected as e:
        print(f"error: {e}")
        messages.error(request, ("Ha ocurrido un error, por favor inténtelo de nuevo más tarde"))
        return redirect(request.META.get('HTTP_REFERER', 'http://127.0.0.1:443') + ("#contact"))

    # Si no es una solicitud POST, simplemente renderiza el formulario
    return redirect(request.META.get('HTTP_REFERER', 'http://127.0.0.1:443') + ("#contact"))



