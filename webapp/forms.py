from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from webapp.codes import VALID_CODES

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'last_name', 'phone', 'country', 'city', 'code', 'company_name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Teléfono'}),
            'country': forms.TextInput(attrs={'placeholder': 'País'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ciudad'}),
            'code': forms.TextInput(attrs={'placeholder': 'Código de uso'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Nombre de la Empresa'}),
        }

class ChangePlan(forms.ModelForm):
    class Meta:
        model = User
        fields = ['code']
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Código de uso'}),
        }

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'custom-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'custom-input'}))

class DeleteUser(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'custom-input'}))

class UserRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'custom-input'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'custom-input'}))
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'class': 'custom-input'}))
    phone = forms.CharField(max_length=9, widget=forms.TextInput(attrs={'class': 'custom-input'}))
    company_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'custom-input'}))
    country = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'custom-input'}))
    city = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'custom-input'}))
    code = forms.CharField(max_length=9, widget=forms.TextInput(attrs={'class': 'custom-input'}))
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        valid_code = next((item for item in VALID_CODES if item['code'] == code), None)
        
        if valid_code is None:
            raise forms.ValidationError('El código proporcionado no es válido')
        if User.objects.filter(code=code).exists():
            raise forms.ValidationError('Este código ya está en uso')
        return code
    
    class Meta:
        model = User
        fields = ['name', 'last_name', 'email', 'phone', 'company_name', 'country', 'city', 'code', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya esta registrado')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])  # Save the password
        
        code = self.cleaned_data['code']
        valid_code = next((item for item in VALID_CODES if item['code'] == code), None)
        
        if valid_code:
            user.plan = valid_code['plan']
            user.plan_start = valid_code['plan_start']
            user.plan_end = valid_code['plan_end']
            user.plan_status = 'Activo'
        else:
            raise forms.ValidationError('El código proporcionado no es válido')

        if commit:
            user.save()
        return user
