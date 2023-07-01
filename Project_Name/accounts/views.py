
# Create your views here.
from django.shortcuts import render , get_object_or_404, redirect
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Preferences


def login(request):
    if request.method == 'POST':
        username= request.POST['username']
        password= request.POST['password']


        user= auth.authenticate(username=username, password= password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, '"كلمة المرور أو اسم المستخدم غير صحيح "')
            return redirect('login')
    else:
        return render(request, "login.html")

def register(request):
    if request.method == "POST":
        first_name= request.POST['first_name']
        last_name= request.POST['last_name']
        username= request.POST['username']
        email= request.POST['email']
        password1= request.POST['password1']
        password2= request.POST['password2']
        allergy = request.POST['allergy']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "اسم المستخدم مستخدم سابقاً")
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request, "الايميل مستخدم سابقاً")
                return redirect('register')

            else:
                user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name,last_name=last_name )
                profile = Preferences.objects.create(user=user
                                                ,allergy = allergy )
                user.save();
                profile.save();
                messages.success(request, "مرحبا \"{}\" تم تسجيلك بنجاح في موقع توت ".format(first_name))
                return redirect('login')
        else:
            messages.info(request, "الرجاء ادخال كلمة مرور صحيحة")
            return render('register')
        return redirect('/')

    else:
        return render(request, "register.html")

def logout(request):
        auth.logout(request)
        return redirect('/')






