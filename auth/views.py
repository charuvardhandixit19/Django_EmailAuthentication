from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from gfg import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from . tokens import generate_token
from django.core.mail import EmailMessage
# Create your views here.
def home(request):
    return render(request,'index.html')
def signup(request):
    if request.method == 'POST':
        # Get form values   
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        password=request.POST['password']
        email=request.POST['email']
        confirmpassword=request.POST['confirmpassword']

        if User.objects.filter(username=username):
            messages.error(request,"Username already exists")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.warning(request,"Email is already exist")
            return redirect('signup')
        
        if len(username)>10:
            messages.error(request,"Username should be under 10 character")

        if password!=confirmpassword:
            messages.error(request,"Password does not match")

        if not username.isalnum():
            messages.error(request="Username must contain alphanumeric characters")
            return redirect('index')

        myuser=User.objects.create_user(username,email,password)
        myuser.first_name=firstname
        myuser.last_name=lastname
        myuser.is_active=False

        myuser.save()
        messages.success(request,"Your Account Has Been Successfully Created")

        #Welcome EMAIL

        subject="Welcome  to login page of our website "
        message="Hello" + myuser.first_name + "!!\n" +"Welcome to our website Please confirm your email account We have sent email to your gmail please confirm it!!!"
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)

        # EMAIL ADDRESS CONFIRMING EMAIL

        current_site=get_current_site(request)
        email_subject="Confirm your email @ login page"
        message2=render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)
        })
        email=EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
            )
        email.fail_silently=True
        email.send()


        return redirect(signin)

    return render(request,'signup.html')
def signin(request):
    if request.method=='POST':
        username = request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            firstname=user.firstname
            return render(request,"index.html",{'firstname':firstname})
        else:
            messages.error(request,"Username Or Password doest't match")
            return redirect('/')

    return render(request,'signin.html') 
def signout(request):
    logout(request)
    messages.success(request,"Logged Out Successfully")
    return redirect("/")

def  activate(request,udib64,token):
    try:
        uid=force_str(urlsafe_base64_decode(udib64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser=None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        return redirect('/')
    else:
        return render(request,'activationfailed.html')