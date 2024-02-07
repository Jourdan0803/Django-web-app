from django.shortcuts import render,redirect
from django import forms
# Create your views here.
from django.http import HttpResponse
from polls.models import UserInfo, OrderInfo
from polls import models
from django.db.models import Func
from django.core.mail import send_mail
from django.conf import settings

from polls.utils.encrypt import md5
from polls import quickstart

import logging
logging.basicConfig(filename='danger_log.txt',
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(obj):
    send_mail(
        "Subject here",
        "Here is the message.",
        "settings.EMAIL_HOST_USER",
        ["jourdan.ljxx@gmail.com"],
        fail_silently=False,    
    )

class CreateForm(forms.Form):
    model = models.UserInfo
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder":"Userword"})

    )
    email = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder":"Email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder":"Password"})

    )
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

class loginForm(forms.Form):
    model = models.UserInfo
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder":"Userword"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder":"Password"})

    )
    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

class UserModelform(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["vehicle_type", "driver_license", "seats_num"]
        widgets = {
            "vehicle_type": forms.TextInput(attrs={"class": "form-control", "placeholder":"Enter your vehicle type"}),
            "driver_license": forms.TextInput(attrs={"class": "form-control", "placeholder":"Enter your driver license"}),
            "seats_num":forms.TextInput(attrs={"class": "form-control", "placeholder":"Enter your vehicle's seats number"})
        }

def get_obj(request):
    info = request.session.get("info")
    userid = info['id']
    obj = UserInfo.objects.filter(id = userid).first()
    return obj



# ***************************************** test page **********************************
def test(request):
    return render(request,"driver_order_info.html")
# ***************************************** test page **********************************

# start page
def start(request):
    return render(request,"start.html")

# login in page
def user_login(request):
    if request.method == "GET":
        form = loginForm()
        return render(request,"user_login.html", {'form':form})
    form = loginForm(data = request.POST)
    if form.is_valid():
        admin_object = models.UserInfo.objects.filter(**form.cleaned_data).first()
        if not admin_object:
            logger.warning("wrong username or password")
            form.add_error("password", "wrong username or password")
            return render(request,"user_login.html", {'form':form})
        request.session["info"] = {'id': admin_object.id, 'name': admin_object.username, 'is_driver':admin_object.is_driver}
        return redirect("/users/home")
    return render(request,"user_login.html", {'form':form})


# sign up page
def user_create(request):
    if request.method == "GET":
        form1 = CreateForm()
        return render(request,"user_create.html", {'form':form1})
    form1 = CreateForm(data = request.POST)
    if form1.is_valid():
        user = form1.cleaned_data.get('username')
        pwd = form1.cleaned_data.get('password')
        email = form1.cleaned_data.get('email')
        exist = UserInfo.objects.filter(username = user).exists()
        if exist:
            logger.warning("username already exist")
            form1.add_error("username", "username already exists")
            return render(request,"user_create.html", {'form':form1})
        UserInfo.objects.create(username = user, password = pwd, email = email)
        return redirect("/users/login")
    else:
        print(form1.errors)
    return render(request,"user_create.html", {'form':form1})

# user home page(after log in)
def user_home(request):
    ob = get_obj(request)
    # send_mail(
    #     "Subject here",
    #     "Here is the message.",
    #     "settings.EMAIL_HOST_USER",
    #     ["jourdan.ljxx@gmail.com"],
    #     fail_silently=False,    
    # )
    return render(request,"user_home.html", {'username': ob.username})

# user log out
def user_logout(request):
    request.session.clear()
    return redirect("/users/login")

# user profile
def user_profile(request):
    ob = get_obj(request)
    driver = ob.is_driver
    userid = ob.id
    if driver == 1:
        return redirect('/driver/profile')
    if request.method == "GET":
        return render(request,"user_profile.html", {'username': ob.username, 'ob':ob})
    if 'edit_username' in request.POST:
        name = request.POST.get("username")
        exist = UserInfo.objects.filter(username = name).exists()
        if not name:
            logger.warning("username cannot be None")
            return render(request,"user_profile.html", {'username': ob.username, 'ob':ob, 'error_meg':"Username can not be none!"})
        if exist:
            logger.warning("username already exist")
            return render(request,"user_profile.html", {'username': ob.username, 'ob':ob, 'error_meg':"Username already exist!"})
        UserInfo.objects.filter(id = userid).update(username = name)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"user_profile.html", {'username': obnew.username, 'ob':obnew, 'meg':"Edit username successfully!"})
    if 'edit_email' in request.POST:
        email = request.POST.get("email")
        if not email:
            logger.warning("email cannot be None")
            return render(request,"user_profile.html", {'username': ob.username, 'ob':ob,'error_meg1':"Email can not be none!"})
        UserInfo.objects.filter(id = userid).update(email = email)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"user_profile.html", {'username': obnew.username, 'ob':obnew, 'meg1':"Edit email successfully!"})

# ************************************************ driver page *********************************************8
def driver_profile(request):
    ob = get_obj(request)
    userid = ob.id
    driver = ob.is_driver
    if driver == 0:
        return redirect('/users/profile')
    if request.method == "GET":
        return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob})
    if 'edit_username' in request.POST:
        name = request.POST.get("username")
        exist = UserInfo.objects.filter(username = name).exists()
        if not name:
            logger.warning("username cannot be None")
            return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob,'error_meg':"Username can not be none!"})
        if exist:
            logger.warning("username already exist")
            return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob, 'error_meg':"Username already exist!"})
        UserInfo.objects.filter(id = userid).update(username = name)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"driver_profile.html", {'username': obnew.username, 'ob':obnew, 'meg':"Edit Username successfully!"})
    if 'edit_email' in request.POST:
        email = request.POST.get("email")
        if not email:
            logger.warning("Email cannot be None")
            return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob,'error_meg3':"Email can not be none!"})
        UserInfo.objects.filter(id = userid).update(email = email)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"driver_profile.html", {'username': obnew.username, 'ob':obnew, 'meg5':"Edit email successfully!"})
    if 'edit_vehicle_type' in request.POST:
        vehicle_type = request.POST.get("type")
        if vehicle_type == "Choose your vehicle type":
            logger.warning("Vehicle type cannot be None")
            return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob, 'error_meg1':"Please choose a vehicle type!"})
        UserInfo.objects.filter(id = userid).update(vehicle_type = vehicle_type)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"driver_profile.html",{'username': obnew.username,'ob':obnew, 'meg1':"Edit vehicle type successfully!"})
    if 'edit_driver_license' in request.POST:
        driver_license = request.POST.get("license")
        if not driver_license:
            logger.warning("Driver license cannot be None")
            return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob,'error_meg4':"Driver license can not be none!"})
        UserInfo.objects.filter(id = userid).update(driver_license = driver_license)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"driver_profile.html", {'username': obnew.username, 'ob':obnew, 'meg2':"Edit driver license successfully!"})
    if 'edit_seats_num' in request.POST:
        seats = request.POST.get("seats")
        if not seats:
            logger.warning("seats cannot be None")
            return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob,'error_meg5':"Seats number can not be none!"})
        UserInfo.objects.filter(id = userid).update(seats_num = seats)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"driver_profile.html", {'username': obnew.username, 'ob':obnew, 'meg3':"Edit seats number successfully!"})
    if 'edit_special_info' in request.POST:
        info = request.POST.get("info")
        if not info or info == "":
            info = "None"
        UserInfo.objects.filter(id = userid).update(special_info = info)
        obnew = UserInfo.objects.filter(id = userid).first()
        return render(request,"driver_profile.html", {'username': obnew.username, 'ob':obnew, 'meg4':"Edit special information successfully!"})
    return render(request,"driver_profile.html", {'username': ob.username, 'ob':ob})


def driver_create(request):
    ob = get_obj(request)
    driver = ob.is_driver
    if driver == 1:
        return redirect('/driver/home')
    if request.method == "GET":
        form = UserModelform()
        return render(request,"driver_create.html", {'username': ob.username, 'form':form})
    vehicle_type = request.POST.get("type")
    driver_license = request.POST.get("license")
    seats = request.POST.get("seats")
    info = request.POST.get("info")
    if vehicle_type == "Please choose your vehicle type":
        logger.warning("Vehicle type cannot be None")
        return render(request,"driver_create.html", {'username': ob.username, 'ob':ob, 'error_meg':"Please choose a vehicle type!"})
    if not driver_license:
        logger.warning("Driver license cannot be None")
        return render(request,"driver_create.html", {'username': ob.username, 'ob':ob, 'error_meg1':"Driver license can not be empty"})
    if not seats:
        logger.warning("seats number cannot be None")
        return render(request,"driver_create.html", {'username': ob.username, 'ob':ob, 'error_meg2':"seats number can not be empty"})
    ob = UserInfo.objects.filter(id = ob.id).update(is_driver=1,driver_license = driver_license,special_info = info, seats_num = seats, vehicle_type = vehicle_type)
    return redirect('/driver/home')


def driver_auth(request):
    ob = get_obj(request)
    driver = ob.is_driver
    if driver == 0:
        return redirect('/driver/signup')
    return redirect('/driver/home')

def driver_signup(request):
    ob = get_obj(request)
    return render(request,"driver_signup.html", {'username': ob.username})

def driver_home(request):
    ob = get_obj(request)
    driver = ob.is_driver
    if driver == 0:
        return redirect('/driver/signup')
    return render(request,"driver_home.html", {'username': ob.username})

class OrderModelForm(forms.ModelForm):
    class Meta:
        model = models.OrderInfo
        fields = ["location", "destination", "date", "time", "time_earlist", "time_latest", "owner_num"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for name, field in self.fields.items():
                field.widget.attrs = {"class": "form-control", "placeholder": field.label}

        def save(self, form, *args, **kwargs):
            super(MyModel, self).save(*args, **kwargs)
            return self.id


def take_ride(request):
    ob = get_obj(request)
    if request.method == "GET":
        form = OrderModelForm()
        return render(request, "take_ride.html", {'username': ob.username, 'ob':ob, 'form': form})

    order_owner = ob.username
    form = OrderModelForm(data=request.POST)
    # print(type(request.POST.get("time")))
    if form.is_valid():

        # other attributes
        vehicle_type = request.POST.get("type")
        is_share = request.POST.get("share")
        info = request.POST.get("info")
        if not info:
            info = "None"
        print(info)
        if vehicle_type == "Choose your vehicle type":
            logger.warning("Vehicle type cannot be None")
            return render(request,"take_ride.html", {'username': ob.username, 'ob':ob, 'error_meg':"Please choose a vehicle type!"})
        if is_share == "Choose Your answer":
            logger.warning("Share cannot be None")
            return render(request,"take_ride.html", {'username': ob.username, 'ob':ob, 'error_meg1':"Please make your decision!"})

        order_id = form.save().id
        ob = OrderInfo.objects.filter(id = order_id).update(info = info, vehicle_type = vehicle_type, is_share=is_share, order_owner=order_owner)
        return redirect("/users/list")
    return render(request, "take_ride.html", {'username': ob.username, 'ob':ob, 'form': form})


def driver_search(request):
    ob = get_obj(request)
    if request.method == "GET":
        allset = models.OrderInfo.objects.all()
        return render(request, "driver_search.html", {'username': ob.username, 'ob':ob ,'allset':allset})
    v_type = request.POST.get("types")
    seats = request.POST.get("seats")
    info = request.POST.get("info")
    if not info:
        info = "None"
    if v_type == "Please choose your vehicle type":
        logger.warning("Vehicle type cannot be None")
        return render(request,"driver_search.html", {'username': ob.username, 'ob':ob, 'error_meg':"Please choose a vehicle type!"})
    if not seats:
        logger.warning("Seats cannot be None")
        return render(request,"driver_search.html", {'username': ob.username, 'ob':ob, 'error_meg1':"seats number can not be empty"})
    #ob = UserInfo.objects.filter(id = ob.id).update(is_driver=1,driver_license = driver_license,special_info = info, seats_num = seats, vehicle_type = vehicle_type)
    queryset = models.OrderInfo.objects.filter(vehicle_type = v_type, is_confirm = False, owner_num__lte = seats, info = info).exclude(order_owner = ob.username)
    if not queryset:
        logger.warning("No match")
        return render(request,"driver_search.html",{'username': ob.username,'ob':ob, 'no_result':"No matched result find"})
    return render(request,"driver_search.html",{'username': ob.username,'ob':ob, 'queryset':queryset})

# def driver_order_info(request, nid):
#     ob = get_obj(request)
#     if request.method == "GET":  
#         obj = models.OrderInfo.objects.filter(id=nid).first() 
#         return render(request, "driver_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj})
#     if request.method == "POST":
#         obj = models.OrderInfo.objects.filter(id=nid)
#         if 'confirm' in request.POST:  
#             obj.update(is_confirm=True, status = "confirmed", driver=ob.username, seats_num=ob.seats_num)
#         if 'complete' in request.POST: 
#             obj.update(status = "complete")
#         return redirect("/driver/list")
def driver_order_info(request, nid):
    ob = get_obj(request)
    if request.method == "GET":  
        obj = models.OrderInfo.objects.filter(id=nid).first() 
        return render(request, "driver_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj})
    if request.method == "POST":
        obj = models.OrderInfo.objects.filter(id=nid)
        obj_email = models.OrderInfo.objects.filter(id=nid).first()
        if 'confirm' in request.POST: 
            sharer1 = models.UserInfo.objects.filter(username = obj_email.order_owner).first()
            sharer2 = models.UserInfo.objects.filter(username = obj_email.share_user).first()
            service = quickstart.gmail_authenticate()
            quickstart.send_message(service, "jourdan.ljxx@gmail.com", sharer1.email, "Confirm email from Wego", "<h1>Your ride has been confirmed by a driver</h1>")
            if sharer2:
                quickstart.send_message(service, "jourdan.ljxx@gmail.com", sharer2.email, "Confirm email from Wego", "<h1>Your ride has been confirmed by a driver</h1>")
            obj.update(is_confirm=True, status = "confirmed", driver=ob.username, seats_num=ob.seats_num)
        if 'complete' in request.POST: 
            obj.update(status = "complete")
        return redirect("/driver/list")


def driver_list(request):
    ob = get_obj(request)
    queryset = models.OrderInfo.objects.filter(is_confirm = True, driver = ob.username)
    return render(request, "driver_list.html", {'username': ob.username, 'ob':ob,'queryset':queryset })


def user_order_info(request, nid):
    ob = get_obj(request)
    obj = models.OrderInfo.objects.filter(id=nid).first() 
    if request.method == "GET":  
        obj = models.OrderInfo.objects.filter(id=nid).first() 
        return render(request, "user_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj})
    if 'edit_location' in request.POST:
        loc = request.POST.get("location")
        if not loc:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj,'error_meg0':"Location can not be none!"})
        OrderInfo.objects.filter(id = nid).update(location=loc)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg0':"Edit location successfully!"})
    if 'edit_destination' in request.POST:
        dest = request.POST.get("destination")
        if not dest:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg1':"Destination can not be none!"})
        OrderInfo.objects.filter(id = nid).update(destination=dest)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg1':"Edit destination successfully!"})
    if 'edit_date' in request.POST:
        date = request.POST.get("date")
        if not date:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg2':"Date can not be none!"})
        OrderInfo.objects.filter(id = nid).update(date=date)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg2':"Edit date successfully!"})
    if 'edit_time' in request.POST:
        time = request.POST.get("time")
        if not time:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg3':"Time can not be none!"})
        OrderInfo.objects.filter(id = nid).update(time=time)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg3':"Edit departure time successfully!"})
    if 'edit_time_earlist' in request.POST:
        time_earlist = request.POST.get("time_earlist")
        if not time_earlist:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg4':"Earliest acceptable departure time can not be none!"})
        OrderInfo.objects.filter(id = nid).update(time_earlist=time_earlist)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg4':"Edit earliest acceptable departure time successfully!"})
    if 'edit_time_latest' in request.POST:
        time_latest = request.POST.get("time_latest")
        if not time_latest:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg5':"Latest acceptable departure time can not be none!"})
        OrderInfo.objects.filter(id = nid).update(time_latest=time_latest)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg5':"Edit latest acceptable departure time successfully!"})
    if 'edit_owner_num' in request.POST:
        owner_num = request.POST.get("owner_num")
        if not owner_num:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg6':"Number of passengers can not be none!"})
        OrderInfo.objects.filter(id = nid).update(owner_num = owner_num)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg6':"Edit number of passengers successfully!"})
    if 'edit_vehicle_type' in request.POST:
        vehicle_type = request.POST.get("vehicle_type")
        if not vehicle_type:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg7':"Please choose your vehicle type!"})
        OrderInfo.objects.filter(id = nid).update(vehicle_type = vehicle_type)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg7':"Edit your desired vehicle type successfully!"})
    if 'edit_is_share' in request.POST:
        is_share = request.POST.get("share")
        if not is_share:
            return render(request,"user_order_info.html", {'username': ob.username, 'ob':ob,'obj':obj,'error_meg8':"Please make your decision on share!"})
        OrderInfo.objects.filter(id = nid).update(is_share = is_share)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg8':"Edit your decision on share successfully!"})
    if 'edit_info' in request.POST:
        info = request.POST.get("info")
        OrderInfo.objects.filter(id = nid).update(info = info)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg9':"Edit your special order info successfully!"})
    if 'cancel' in request.POST:
        OrderInfo.objects.filter(id = nid).delete()
        return redirect("/users/list")
    if 'cancel_share' in request.POST:
        all_num = OrderInfo.objects.filter(id = nid).first().owner_num - OrderInfo.objects.filter(id = nid).first().share_num
        OrderInfo.objects.filter(id = nid).update(share_num=0, share_user = None, owner_num=all_num)
        return redirect("/users/list")
    if 'edit_share_num' in request.POST:
        share_num = request.POST.get("share_num")
        if not share_num or share_num == "":
            obj = OrderInfo.objects.filter(id = nid).first()
            return render(request,"user_order_info.html", {'username': obj.share_user, 'obj':obj,'ob':ob,'obj':obj,'error_meg10':"Please enter your sharer number!"})
        share_num = int(share_num)
        all_num = OrderInfo.objects.filter(id = nid).first().owner_num - OrderInfo.objects.filter(id = nid).first().share_num + share_num
        OrderInfo.objects.filter(id = nid).update(share_num = share_num,owner_num = all_num)
        objnew = OrderInfo.objects.filter(id = nid).first()
        return render(request,"user_order_info.html", {'username': ob.username, 'obj':objnew, 'meg10':"Edit your sharer number successfully!"})
        
    return render(request, "user_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj})

def user_list(request):
    ob = get_obj(request)
    queryset = models.OrderInfo.objects.filter(order_owner = ob.username)
    shareset = models.OrderInfo.objects.filter(share_user = ob.username)
    return render(request, "user_list.html", {'username': ob.username, 'ob':ob,'queryset':queryset,'shareset':shareset })


def sharer_search(request):
    ob = get_obj(request)
    if request.method == "GET":
        return render(request, "sharer_search.html", {'username': ob.username, 'ob':ob })
    destination = request.POST.get("destination")
    date = request.POST.get("date")
    passengers = request.POST.get("passengers")
    time_earlist = request.POST.get("time_earlist")
    time_latest = request.POST.get("time_latest")
    if not destination:
        return render(request,"sharer_search.html", {'username': ob.username, 'ob':ob, 'error_meg':"Destination can not be empty!"})
    if not date:
        return render(request,"sharer_search.html", {'username': ob.username, 'ob':ob, 'error_meg1':"Please choose a date!"})
    if not passengers:
        return render(request,"sharer_search.html", {'username': ob.username, 'ob':ob, 'error_meg2':"Passengers number can not be empty!"})
    if not time_earlist or not time_latest:
        return render(request,"sharer_search.html", {'username': ob.username, 'ob':ob, 'error_meg3':"Please choose the arrival time window"})
    #ob = UserInfo.objects.filter(id = ob.id).update(is_driver=1,driver_license = driver_license,special_info = info, seats_num = seats, vehicle_type = vehicle_type)
    queryset = models.OrderInfo.objects.filter(share_user = None, is_share = True, destination = destination, date = date, is_confirm = False,time_earlist__gte = time_earlist, time_latest__lte=time_latest).exclude(order_owner = ob.username)
    if not queryset:
        return render(request,"sharer_search.html",{'username': ob.username,'ob':ob, 'no_result':"No matched result find"})
    OrderInfo.objects.filter(id = ob.id).update()
    return render(request,"sharer_search.html",{'username': ob.username,'queryset':queryset,'passengers':passengers})


def user_share_order_info(request, nid, passengers):
    ob = get_obj(request)
    if request.method == "GET":  
        obj = models.OrderInfo.objects.filter(id=nid).first() 
        return render(request, "user_share_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj, 'passengers': passengers})
    if request.method == "POST":
        if 'join' in request.POST:
            all_num = OrderInfo.objects.filter(id = nid).first().owner_num + passengers
            OrderInfo.objects.filter(id = nid).update(share_num=passengers, share_user = ob.username, owner_num=all_num)
        return redirect("/users/list")
        # return render(request, "user_share_order_info.html", {'username': ob.username, 'ob':ob, 'obj':obj})