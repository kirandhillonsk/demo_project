from cmath import log
import csv
from datetime import datetime
import re
from time import time
from django.views import View
import xlwt
from tokenize import Token
from pytz import timezone
from accounts.forms import SubscriptionForm
from contact.models import ContactUs
from enduser.constants import PAGE_COUNT
from enduser.models import *
from frontend.models import Join_Us
from notification.models import Notification
from rating.models import Rating
from rvt_lvt.models import *
from accounts.models import *
from accounts.constants import *
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from superuser.models import  Announcements, Banners, HelpTopics, JobOpenings, NewsletterSubscription, Recommendation, Tax, Mileage
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Q
import time
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sessions.models import Session
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from geopy.geocoders import Nominatim
from weasyprint import HTML
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import environ
env = environ.Env()
environ.Env.read_env()
import stripe
stripe.api_key = env('STRIPE_KEY')
env = environ.Env()
environ.Env.read_env()
from global_utils import *
from django.urls import reverse_lazy, path



"""
View Announcement
"""
@login_required
def ViewAnnouncement(request):
    try:
        announcement=Announcements.objects.get(id=request.GET.get("id"))
        return render(request, 'admin/view-announcement.html',{"title":"Announcement Details", "nbar" : "announcements","announcement":announcement})
    except:
        announcement=None


"""
Edit Announcement
"""
@login_required
def EditAnnouncement(request):
    if request.method == 'GET':
        try:
            announcement=Announcements.objects.get(id=request.GET.get("id"))
            return render(request, 'admin/edit-announcements.html',{"title":"Edit Announcement", "nbar" : "announcements","announcement":announcement})
        except:
            announcement=None
    if request.method == 'POST':
        try:
            announcement=Announcements.objects.get(id=request.POST.get("id"))
        except:
            announcement=None
        if announcement:
            announcement.title =request.POST.get("title")
            announcement.description =request.POST.get("description")
            announcement.status =request.POST.get("status")
            announcement.target =request.POST.get("target")
            announcement.created_by_id =request.user.id
            if request.FILES.get("image"):
                announcement.image = request.FILES.get("image")
            announcement.save()
            messages.add_message(request, messages.INFO, 'Announcement Updated Successfully')
        return redirect('superuser:announcement_list')


"""
Reset Customer Id's
"""
def ResetCustomerIds(request):
    User.objects.all().exclude(role_id=ADMIN).update(bank_account_id = None)
    users = User.objects.all().exclude(role_id=ADMIN)
    for user in users:
        try:
            stripe_customer = stripe.Customer.create(
                description = " space User - %s " % user.email,
                email = user.email
            )
            user.customer_id = stripe_customer.id
            user.save()
        except Exception as e:
            pass
    messages.add_message(request, messages.INFO, "Customer Id's Reset Successfully!")
    return redirect('accounts:users_list')


"""
edit user
"""
@login_required
def AdminEditUserProfile(request):
    if request.method == 'GET':
        API_KEY=env('GOOGLE_API_KEY')
        user = User.objects.get(id = request.GET.get("user"))
        appointments_complete_count=Appointments.objects.filter(created_for=user,status=COMPLETED).count
        return render(request, 'admin/admin-edit-user-profile.html',{"user":user,"title":"Users","nbar" : "users_list","API_KEY":API_KEY,"appointments_complete_count":appointments_complete_count})
    if request.method == 'POST':
        user = User.objects.get(id = request.POST.get("user_id"))

        if request.POST.get("first_name"):
            user.first_name = request.POST.get("first_name")

        if request.POST.get("last_name"):
            user.last_name = request.POST.get("last_name")

        if request.POST.get("address"):
            user.address = request.POST.get("address")

        if request.POST.get("city"):
            user.city = request.POST.get("city")

        if request.POST.get("state"):
            user.state = request.POST.get("state")
        
        if request.POST.get("latitude"):
            user.latitude = request.POST.get("latitude")

        if request.POST.get("longitude"):
            user.longitude = request.POST.get("longitude")

        if request.POST.get("about_me"):
            user.about_me = request.POST.get("about_me")

        user.save()
        messages.add_message(request, messages.INFO, 'User Updated Successfully')
        return redirect('superuser:users_list')
    


@login_required
def GetUserState(request):
    data = {"state":""}
    try:
        lat = request.GET.get("lat")
        long = request.GET.get("long")
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(lat+","+long)
        state = location.raw['address']['state']
        country=location.raw ['address']['country']
        city=location.raw ['address']['city']

        data['state'] = state
        data['country'] = country
        data['city'] = city
    except:
        data['state'] = ''
        data['country'] = ''
        data['city'] = ''
    return JsonResponse(data)

"""
admin profile
"""
@login_required
def AdminProfile(request):
    if request.method == 'GET':
        try:
            API_KEY=env('GOOGLE_API_KEY')
            user = User.objects.get(id = request.user.id)
            return render(request, 'admin/admin-profile.html',{"user":user,"API_KEY":API_KEY})
        except:
            return redirect('accounts:web_login')
    if request.method == 'POST':
        user = User.objects.get(id = request.user.id)
        
        if request.POST.get("username"):
            user.username = request.POST.get("username")
        
        if request.POST.get('firstname'):
            user.first_name=request.POST.get('firstname')
        
        if request.POST.get('lastname'):
            user.last_name=request.POST.get('lastname')

        if request.POST.get("address"):
            user.address = request.POST.get("address")

        if request.POST.get("longitude"):
            user.longitude = request.POST.get("longitude")

        if request.POST.get("latitude"):
            user.latitude = request.POST.get("latitude")

        if request.POST.get("city"):
            user.city = request.POST.get("city")

        if request.POST.get("state"):
            user.state = request.POST.get("state")

        if request.POST.get("about_me"):
            user.about_me = request.POST.get("about_me")
        
        if request.POST.get("email"):
            user.email = request.POST.get("email")

        user.save()
        messages.add_message(request, messages.INFO, 'Profile Updated Successfully')
        return redirect('superuser:admin_profile')


"""
edit profile_pic
"""
@login_required
def AdminProfileImage(request):
    if request.method == 'POST':
        user = User.objects.get(id = request.user.id)

        file = str(request.FILES.get("profile_pic"))
        
        if not file.endswith('.png'):
            messages.add_message(request, messages.INFO, 'This file extention is not supported')
            return redirect('superuser:admin_profile')

        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES.get("profile_pic")

        user.save()
        messages.add_message(request, messages.INFO, 'Profile Image Updated Successfully')
        return redirect('superuser:admin_profile')




"""
Pervious details
"""
@login_required
def PreviousCategoryData(request):
    if request.is_ajax():
        category_id  = request.GET.get("category_id")
        category = ServiceCategory.objects.get(id=category_id)
        if category:
            data = {
                "id":category.id,
                "title":category.title,
                "description":category.description,
            }
            return JsonResponse(data)


"""
Pervious details
"""
@login_required
def PreviousPettypeData(request):
    if request.is_ajax():
        category_id  = request.GET.get("category_id")
        category = PetType.objects.get(id=category_id)
        if category:
            data = {
                "id":category.id,
                "title":category.name,
            }
            return JsonResponse(data)

"""
User list
"""
@login_required
def UsersList(request):
    users = User.objects.filter(Q(role_id = USERS)|Q(role_id = RVT_LVT)).exclude(role_id = ADMIN).order_by('-created_on')
    try:
        page = request.GET.get('page', 1)
        paginator = Paginator(users, 10)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    except Exception as e:
        users = None
    badge = Badge.objects.all()
    return render(request,'admin/users-list.html',{"title":"Users", "nbar" : "users_list","users":users,"badge":badge})


"""
Rvt User List
"""
@login_required
def RvtuserList(request):
    users = User.objects.filter(applied_for = RVT_LVT).order_by('-created_on')
    try:
        page = request.GET.get('page', 1)
        paginator = Paginator(users, 10)
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    except Exception as e:
        users = None
    return render(request,'admin/rvt-users-list.html',{"title":"Rvt Applications", "nbar" : "rvt_users","users":users})


"""
accpet reject rvt application
"""
@login_required
def AccpetRjectApplication(request):
    if request.method == 'POST':
        if request.POST.get("status"):
            user = User.objects.get(id = request.POST.get("user_id"))
            user.is_verified = int(request.POST.get("status"))
            user.save()   
            Session.objects.filter(session_key = user.session_id).delete()
            if request.POST.get("status") == '1':
                msg = 'You accept the rvt application'
                user.session_id = ''
                user.user_to_rvt= 1
                user.role_id = 3
                user.save()
                if user.is_push:
                    Notification.objects.create(
                        title = "RVT Application",
                        description = " Your application to become an RVT is approved. You can now switch to RVT profile.",
                        created_by =request.user,
                        created_for_id=user.id,
                    )      
                current_site = get_current_site(request)
                next_page=reverse_lazy("enduser:user_rvt_profile")
                context = {
                    'domain':current_site.domain,
                    'site_name': current_site.name,
                    'protocol': 'https' if USE_HTTPS else 'http',
                    'protocol': 'https' if USE_HTTPS else 'http',
                    'text':'Congratulations! Your  spaceand Fido RVT application has been approved. Click on below link to login',
                    'login_button':True,
                    'text_title':'Congratulations!!',
                    'next_page': next_page
                }
                message = render_to_string('registration/verify-account-email.html', context)
                mail_subject = 'Application Approved!!'
                to_email = user.email
                email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
                html_email = render_to_string('registration/verify-account-email.html',context)
                email_message.attach_alternative(html_email, 'text/html')
                email_message.send()
            else:
                user = User.objects.get(id = request.POST.get("user_id"))
                user.role_id = 2
                user.applied_for = 0
                user.user_to_rvt  = 0
                msg = 'You have declined the rvt application'
                user.save()   
                if user.is_push:
                    Notification.objects.create(
                        title = "RVT Application",
                        description = "Your request has been declined by admin",
                        created_by =request.user,
                        created_for_id=user.id,
                    )
            messages.error(request, msg)
            return redirect('superuser:rvt_users')


@login_required
def RejectApplication(request,id):
    user = User.objects.get(id = id)
    user.is_verified = REJECT_RVT
    user.role_id = 2
    user.save()
    Session.objects.filter(session_key = user.session_id).delete()
    msg = 'You reject the rvt application'
    current_site = get_current_site(request)
    context = {
        'domain':current_site.domain,
        'site_name': current_site.name,
        'protocol': 'https' if USE_HTTPS else 'http',
        'name': user.first_name + '' + user.last_name,
        'text':'Your  spaceand Fido RVT application has been rejected. Please contact admin@ spaceandfido.org for additional details.',
        'text_title':'Oops !!'
    }
    message = render_to_string('registration/verify-account-email.html', context)

    mail_subject = 'Application Rejected'
    to_email = user.email
        
    email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
    html_email = render_to_string('registration/verify-account-email.html',context)
    email_message.attach_alternative(html_email, 'text/html')
    email_message.send()

    messages.error(request, msg)
    return redirect('superuser:rvt_users')    


"""
User delete
"""
@login_required
def UserDelete(request):
    if request.method == 'GET':
        user = User.objects.get(id = request.GET.get("id"))
        if user.role_id == USER:
            if user:
                user.state_id = DELETED
                user.save()
                messages.add_message(request, messages.INFO, 'User deleted successfully')
                redirect('superuser:users_list')
        else:
            if user:
                user.state_id = DELETED
                user.save()
                messages.add_message(request, messages.INFO, 'Rvt deleted successfully')
                redirect('superuser:rvt_users')

    return render(request,'admin/users-list.html',{"title":"Users", "nbar" : "users_list"})


"""
search user
"""
@login_required
def UserSearch(request):
    if request.method == "GET":
        try:
            search=request.GET.get('user_name')
            d = {'first_name':request.GET.get("user_name"),"state_id" :request.GET.get("state_id")}
            syn = "SELECT * FROM tbl_user WHERE "
            k =[]
            query = ""
            for i in d.keys():
                if d[i]:
                    k.append('%'+d[i]+"%")
                    query += i + " LIKE %s and "
                if i == 'state_id':    
                    if d[i]:
                        k.append(d[i])
                        query += i + " = %s and " 
                else:
                    pass
            query = query.rstrip(" and")
            syn += query
            searclist=[]
            for user in User.objects.raw(syn,k):
                searclist.append(user.id)
            users = User.objects.filter(id__in = searclist)
            badge = Badge.objects.all()

            if request.GET.get('reset')=='reset':
                return redirect('superuser:users_list')

            if users:
                return render(request,'admin/users-list.html',{"search":search,"users":users,"title":"Users", "nbar" : "users_list",'first_name':request.GET.get("user_name"),"state_id" :request.GET.get("state_id"),"badge":badge})
            else:
                messages.add_message(request, messages.INFO, 'No User Found')
                return render(request,'admin/users-list.html',{"search":search,"users":users,"title":"Users", "nbar" : "users_list",'first_name':request.GET.get("user_name"),"state_id" :request.GET.get("state_id"),"badge":badge})
        except:
            messages.add_message(request, messages.INFO, 'Please Enter Something To Search')
            return redirect('superuser:users_list')




"""
admin services
"""
def AdminServices(request):
    services = ServiceCategory.objects.all().order_by('-created_on')
    return render(request,'admin/services.html',{"services":services,"title":"Services", "nbar" : "services"})


"""
admin Pet type
"""
def AdminPetType(request):
    pettype = PetType.objects.all().order_by('-created_on')
    return render(request,'admin/pet-type.html',{"pettype":pettype,"title":"Pet Type", "nbar" : "pettype"})


"""
Add pet type
"""
@login_required
def AddPetType(request):
    if request.method =="POST":
        if PetType.objects.filter(name = request.POST.get("name")):
            messages.add_message(request, messages.INFO, 'Pet type Already Exist')
            return redirect('superuser:admin_pet_type')
        pet_type = PetType.objects.create(
            name = request.POST.get("name"),
            created_by  =request.user
        )
        pet_type.save()
        messages.add_message(request, messages.INFO, 'Pet type Added Successfully')
        return redirect('superuser:admin_pet_type')


"""
delete pet type
"""
@login_required
def DeletePettype(request):
    if request.method =="GET":
        pettype = PetType.objects.get(id = request.GET.get("id"))
        service = Services.objects.filter(pet_id = pettype.id)
        if service:
            messages.add_message(request, messages.INFO, 'This pet type exist in serivces, You can not delete this')
            return redirect('superuser:admin_pet_type')
        else:
            if pettype:
                pettype.delete()
                messages.add_message(request, messages.INFO, 'Pettype Deleted Successfully')
                return redirect('superuser:admin_pet_type')

"""
edit pet type
"""
@login_required
def PettypeEdit(request):
    if request.method == 'POST':
        pettype =  PetType.objects.get(id=request.POST.get("category_id"))
        if request.POST.get("name",None):
            pettype.name = request.POST.get("name")
        pettype.save()
        messages.error(request, 'Pet type Updated Successfully')
        return redirect('superuser:admin_pet_type')



"""
Add Service Categories
"""
@login_required
def AddServicecategory(request):
    if request.method =="POST":

        if ServiceCategory.objects.filter(title = request.POST.get("title")):
            messages.add_message(request, messages.INFO, 'Service Category Already Exist')
            return redirect('superuser:admin_services')

        service_categories = ServiceCategory.objects.create(title = request.POST.get("title"),description = request.POST.get("description"))
        if request.FILES.get("image"):
            service_categories.image =request.FILES.get("image")
        service_categories.save()
        messages.add_message(request, messages.INFO, 'Service Category Added Successfully')
        return redirect('superuser:admin_services')




"""
delete Service Categories
"""
@login_required
def DeleteServicecategory(request):
    if request.method =="GET":
        categories = ServiceCategory.objects.get(id = request.GET.get("id"))
        service = Services.objects.filter(category_id = categories.id)
        if service:
            messages.add_message(request, messages.INFO, 'Service already exist in services, You can not delete')
            return redirect('superuser:admin_services')
        else:
            if categories:
                categories.delete()
                messages.add_message(request, messages.INFO, 'Service Category Deleted Successfully')
                return redirect('superuser:admin_services')

"""
search service categories
"""
@login_required
def SearchServicecategory(request):
    if request.method=="GET":
        services=request.GET.get('title')
        if not services:
             messages.add_message(request,messages.INFO,'Please enter something to search')
             return redirect('superuser:admin_services')
        elif request.GET.get('reset')=='reset':
             messages.add_message(request,messages.INFO,'Please enter something to search')
             return redirect('superuser:admin_services')
        service= services = ServiceCategory.objects.filter(title__icontains=services)
    return render(request,'admin/services.html',{"search":request.GET.get("title"),"services":service,"title":"Services", "nbar" : "services"})

"""
search service categories
"""
@login_required
def SearchSubAdmin(request):
    if request.method=="GET":
        email=request.GET.get('email')
        if not email:
             messages.add_message(request,messages.INFO,'Please enter somethimng to search')
             return redirect('superuser:sub_admin')
        elif request.GET.get('reset')=='reset':
            messages.add_message(request,messages.INFO,'Please enter somethimng to search')
            return redirect('superuser:sub_admin')
        sub_admins = User.objects.filter(email__icontains=email, role_id = SUB_ADMIN).order_by('-id')
        return render(request,'admin/sub-admin.html',{"search":request.GET.get("email"),"sub_admins":sub_admins,"title":"Sub Admin", "nbar" : "sub-admin"})
    


    
"""
search pet type
"""
@login_required
def SearchPetType(request):
    if request.method=="GET":
        name=request.GET.get('name')
        if not name:
            messages.add_message(request,messages.INFO,'Please enter something to search')
            return redirect('superuser:admin_pet_type')
        elif request.GET.get('reset')=="reset":
            messages.add_message(request,messages.INFO,'Please enter something to search')
            return redirect('superuser:admin_pet_type')
        pets=PetType.objects.filter(name__icontains=name)
        return render(request,'admin/pet-type.html',{"search":request.GET.get("name"),"pettype":pets,"name":"Pets", "nbar" : "pets","title":"Pet Type"})
      

"""
edit service
"""
@login_required
def ServiceCategoryEdit(request):
    if request.method == 'POST':

        category =  ServiceCategory.objects.get(id=request.POST.get("category_id"))

        if request.POST.get("title",None):
            category.title = request.POST.get("title")

        if request.POST.get("description",None):
            category.description = request.POST.get("description")

        if request.FILES.get("image",None):
            category.image = request.FILES.get("image")

        category.save()
        messages.error(request, 'Service Category Updated Successfully')
        return redirect('superuser:admin_services')


"""
view appointment
"""
@login_required
def AppointmentManagement(request):
    try:
        appointments = Appointments.objects.all().order_by('-created_on')
        page = request.GET.get('page', 1)
        paginator = Paginator(appointments, 10)
        try:
            appointments = paginator.page(page)
        except PageNotAnInteger:
            appointments = paginator.page(1)
    except EmptyPage:
        appointments = paginator.page(paginator.num_pages)

    except Exception as e:
        appointments = None
    
    return render(request,'admin/appointments.html',{"appointments":appointments,"title":"Appointments", "nbar" : "appointment_management"})




"""
Search RVT
"""
def SearchRVT(request):
    search =request.GET.get("search")
    date =request.GET.get("date_filter")
    if search:
        search = Appointments.objects.filter(created_for_id__first_name__icontains = request.GET.get("search")).order_by('-created_on')      
        return render(request,'admin/appointments.html',{"appointments":search,"title":"Appointments", "nbar" : "appointment_management"})
    elif date:
        search = Appointments.objects.filter(date__contains = request.GET.get("date_filter")).order_by('-created_on')
        return render(request,'admin/appointments.html',{"appointments":search,"title":"Appointments", "nbar" : "appointment_management"})
    else:
        messages.add_message(request,messages.INFO,"Please Enter Something To Search")
        return redirect("superuser:appointment_management")

"""
Date filter
"""
def DateFilter(request):
    search = Appointments.objects.filter(date__contains = request.GET.get("date_filter")).order_by('-created_on')
    return render(request,'admin/appointments.html',{"appointments":search,"title":"Appointments", "nbar" : "appointment_management"})

"""
Sort filter
"""
@login_required
def Sortfilter(request):
    if request.GET.get('sort_name')== 'date':
        search = Appointments.objects.all().order_by('-date')
        return render(request,'admin/appointments.html',{"appointments":search,"title":"Appointments", "nbar" : "appointment_management"})

    elif request.GET.get('sort_name')== 'name':
        search = Appointments.objects.all().order_by('-created_for__first_name')
        return render(request,'admin/appointments.html',{"appointments":search,"title":"Appointments", "nbar" : "appointment_management"})

    elif request.GET.get('sort_name')== 'status':
        search = Appointments.objects.all().order_by('-date')
        return render(request,'admin/appointments.html',{"appointments":search,"title":"Appointments", "nbar" : "appointment_management"})
    return render(request,'admin/appointments.html',{"appointments":search,"title":"Appointments", "nbar" : "appointment_management"})



""" 
announcement
"""
def AnnouncementsList(request):
    announcement = Announcements.objects.all().order_by('-id')
    return render(request,'admin/announcements.html',{"announcement":announcement,"title":"Announcements", "nbar" : "announcements"})



"""
add appointment
"""
@login_required
def AddAnnouncementView(request):
    if request.method == 'GET':
        return render(request, 'admin/add-announcement.html',{"title":"Add Announcement", "nbar" : "announcements"})

    if request.method == "POST":
        announce = Announcements.objects.create(
            title = request.POST.get("title"),
            description = request.POST.get("description"),
            status = request.POST.get("status"),
            target = request.POST.get("target"),
            created_by_id = request.user.id
        )
        if request.FILES.get("image"):
            announce.image = request.FILES.get("image")
        announce.save()
        if request.POST.get("target")=='1' and request.POST.get("status")=='1' :
            email_list = User.objects.filter(role_id=2).values_list('email',flat=True)
        elif request.POST.get("target")=='2' and request.POST.get("status")=='1':
            email_list = User.objects.filter(role_id=3).values_list('email',flat=True)
        elif request.POST.get("target")=='3' and request.POST.get("status")=='1':
            email_list = User.objects.all().values_list('email',flat=True).exclude(Q(role_id=ADMIN)|Q(role_id=SUB_ADMIN))
        else:
            email_list = None
        if email_list:
            for i in email_list: 
                current_site = get_current_site(request)
                context = {
                    'domain':current_site.domain,
                    'site_name': current_site.name,
                    'protocol': 'https' if USE_HTTPS else 'http',
                    'name':announce.created_by.first_name,
                    'announcement_title':announce.title,
                    'announcement_description':announce.description,
                }
                message = render_to_string('admin/announcement_mail.html', context)
                mail_subject = 'New Announcement Added'
                try:
                    email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [i])
                    html_email = render_to_string('admin/announcement_mail.html',context)
                    email_message.attach_alternative(html_email, 'text/html')
                    email_message.send()
                except:
                    pass
        messages.error(request, 'Announcement Added Successfully')
        return redirect('superuser:announcement_list')


"""
change status
"""
@login_required
def ChangeStatus(request):
    announcement = Announcements.objects.get(id = request.POST.get("status_id"))
    if int(request.POST.get("select_status")) == 1:
        if announcement:
            announcement.status = True
            announcement.save()
            return redirect('superuser:announcement_list')

        if Announcements.objects.filter(status = 1,target=TARGET_USER):
            email_list = User.objects.filter(role_id=2).values_list('email',flat=True)
        elif Announcements.objects.filter(status = 1,target=TARGET_RVT):
            email_list = User.objects.filter(role_id=3).values_list('email',flat=True)
        elif Announcements.objects.filter(status = 1,target=TARGET_ALL):
            email_list = User.objects.all().values_list('email',flat=True).exclude(Q(role_id=ADMIN)|Q(role_id=SUB_ADMIN))

        for i in email_list:
            current_site = get_current_site(request)
            context = {
                'domain':current_site.domain,
                'site_name': current_site.name,
                'protocol': 'https' if USE_HTTPS else 'http',
                'name':announcement.created_by.first_name,
                'announcement_title':announcement.title,
                'announcement_description':announcement.description,
            }
            message = render_to_string('admin/announcement_mail.html', context)
            mail_subject = 'New Announcement Added'
            email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [i])
            html_email = render_to_string('admin/announcement_mail.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
        return redirect('superuser:announcement_list')
    elif int(request.POST.get("select_status")) == 0:
        if announcement:
            announcement.status = False
            announcement.save()
            return redirect('superuser:announcement_list')

"""
Delete announcement
"""
@login_required
def DeleteAnnouncement(request):
    announcement = Announcements.objects.get(id = request.GET.get("id"))
    if announcement:
        announcement.delete()
        messages.error(request, 'Accouncement Deleted Successfully')
        return redirect('superuser:announcement_list')

"""
change announcement status
"""
def ChangeTarget(request):
    announcement = Announcements.objects.get(id = request.POST.get("id"))
    target = request.POST.get("select_target")
    if announcement:
        announcement.target = target
        announcement.save()
        return redirect('superuser:announcement_list')



"""
filter announcement
"""
@login_required
def FilterAnnouncement(request):
    if request.method == "GET":
        try:
            d = {'title':request.GET.get("title"),"status" :request.GET.get("status")}
            search = request.GET.get("title")
            syn = "SELECT * FROM tbl_announcements WHERE "
            k =[]
            query = ""
            for i in d.keys():
                if d[i]:
                    k.append(d[i]+"%")
                    query += "`"+i+"`" + " LIKE %s and"
                else:
                    pass
            query = query.rstrip(" and")
            syn += query
            searclist=[]
            for anc in Announcements.objects.raw(syn,k):
                searclist.append(anc.id)
            announcement = Announcements.objects.filter(id__in = searclist)

            if announcement:
                return render(request, "admin/announcements.html", {"announcement":announcement,"title":"Announcements", "nbar" : "announcements","search":search,"status" :request.GET.get("status")})
            else:
                messages.add_message(request, messages.INFO, 'No Announcement Found')
                return render(request, "admin/announcements.html", {"announcement":announcement,"title":"Announcements", "nbar" : "announcements","search":search,"status" :request.GET.get("status")})
        except:
            messages.add_message(request, messages.INFO, 'Please Enter Something To Search')
            return redirect('superuser:announcement_list')





"""
Email Validation
"""
def Email_Validation(request):
    if request.is_ajax():
        data ={"valid":None,"exists":None,"empty":None}
        email = request.GET.get("email_id")
        pat = r'^[a-zA-Z0-9_.+-]+[@]\w+[.]\w{2,3}$'
        match = str(re.search(pat,email))
        try:
            user_email = User.objects.filter(email=email).last()
            if email == user_email.email:
                data['exists'] = '1'
        except:
            user_email = None
        if email == '':
            data['empty'] = '1'

        if user_email == None:
            data['exists'] = '0'    
        
        if match == "None":
            data['valid'] = '0'
        else:
            data['valid'] = '1'
        return JsonResponse(data)


def SubscribedUser(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = Subscription.objects.create(email = request.POST.get("email"))
            return redirect('frontend:career')
    else:
        form = SubscriptionForm()
    return render(request, 'frontend/career.html', {'form': form,"value":"Value"})

def ContactUSView(request):
    contact_details = ContactUs.objects.all()
    return render(request,'admin/contact.html',{"contact":contact_details,"title":"Contact us","nbar" : "contact_us"})


"""
user_appointment_details 
"""
@login_required
def User_AppointmentDetails(request):
    appointment = Appointments.objects.get(id = request.GET.get('id'))
    appointment_services = Appointments.service.through.objects.filter(appointments_id = appointment).values_list("services_id",flat=True)
    appointment_pet = Appointments.pet.through.objects.filter(appointments_id = appointment).values_list("pets_id",flat=True)
    service = Services.objects.filter(id__in = appointment_services)
    appointment_custom_services = Appointments.custom.through.objects.filter(appointments_id = appointment).values_list("customservice_id",flat=True)
    rvt_cus_service = CustomService.objects.filter(id__in = appointment_custom_services,created_by = appointment.created_for)
    pet = Pets.objects.filter(id__in = appointment_pet)
    notes = Notes.objects.filter(appointment_id = appointment,type = PUBLIC )
    app_custom_services = Appointments.custom.through.objects.filter(appointments_id = appointment).values_list("customservice_id",flat=True)
    cus_service = CustomService.objects.filter(id__in= app_custom_services, created_by = appointment.created_by)
    rating = Rating.objects.filter(appointment=appointment, created_for=appointment.created_for)
    time, distance, distance_km=get_distance_from_coordinates(appointment.created_for.latitude,appointment.created_for.longitude,appointment.created_by.latitude,appointment.created_by.longitude)
    return render(request , "admin/user_appointments_details.html" , {"nbar" : "user_my_appointments","title":"Appointment Details","appointment":appointment,"service":service,"pets":pet,"notes":notes,"cus_service":cus_service,"rvt_cus_service":rvt_cus_service,"distance":distance,"time":time,"rating":rating})


"""
Revert Mail
"""

def mail_revert(request):
    return render(request,"admin/mail_revert.html",{"title":"Revert Message"})


"""
Print Apoointment
"""
def Print_appointment(request):
    DATETIME = time.strftime('%Y%m%d-%H%M%S')
    name= " space_and_Fido" + DATETIME
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename= '+ name +".csv"
    writer = csv.writer(response)
    writer.writerow(['Appointment ID','Customer_Name','RVT','Address','Appointment_Status'])
    month=datetime.now().month
    service=Appointments.objects.filter(date__month=month).values_list("id","created_by__first_name","created_for__first_name","created_by__address","status")
    for appointment in service:
        writer.writerow(appointment)
    return response


"""
Delete Appointment From admin Index
""" 
def delete_appointment_admin_index(request):
    data= {'msg' :None}
    ids = str(request.GET.get('ids'))
    ids = [int(i) for i in ids.split(",")]
    for i in ids:
        app = Appointments.objects.get(id=i)
        app.delete()
    return JsonResponse(data)

"""
Assign Badge
"""
def AssignBadge(request):
    user = User.objects.get(id =request.POST.get('user_id'))
    if user:
        user.badge_id = request.POST.get('badge_input')
        user.save()
        messages.add_message(request, messages.INFO, 'Badge assigned Successfully')
        return redirect('superuser:users_list')
    return redirect('superuser:users_list')


"""
Search in appointment index
"""
def Search_index_admin(request):
    if request.GET.get('search'):
        data = {"id" :[],"services"  :[],"cust_service":[],"created_by" :[],"address": [],"created_for" :[],"status" :[],"amount":[]}
        appointments=Appointments.objects.filter(Q(created_for__first_name__icontains=request.GET.get('search',None))|Q(created_by__first_name__icontains=request.GET.get('search',None))|Q(created_by__address__icontains=request.GET.get('search',None))).order_by('-created_on')
        service_list=""
        custom_service_list=""
        for appointment in appointments:
            service_list=''
            app_service=Appointments.service.through.objects.filter(appointments_id = appointment.id)
            for service in app_service:
                cat = service.services.category.title + '<br>'
                service_list += cat
            custom_service = Appointments.custom.through.objects.filter(appointments_id = appointment.id)
            for services in custom_service:
                ser=services.customservice.title +'<br>'
                custom_service_list =ser
            data['id'].append(appointment.id) 
            data['services'].append(service_list)
            data['cust_service'].append(custom_service_list)
            data['created_by'].append(appointment.created_by.first_name)  
            data['address'].append(appointment.created_by.address)
            data['created_for'].append(appointment.created_for.first_name)
            data['amount'].append(appointment.amount)
            data['status'].append(appointment.status)
        return JsonResponse(data,safe=False)

"""
Recommandations
"""
def recommendation(request):
    recommendation=Recommendation.objects.all().order_by("-created_on")
    category=ServiceCategory.objects.all()
    help_topics = HelpTopics.objects.all().order_by('-created_on')
    return render(request,"admin/recommendation.html",{'nbar':'recommendation',"title":"Recommendation","category":category,"recommendation":recommendation,"help_topics":help_topics})

"""
Create reccommendatation
"""
@login_required
def Create_recommendation(request):
    if request.method=="POST":
        if request.POST.get("category"):
            category = ServiceCategory.objects.get(id = request.POST.get("category"))
        try:
            help_type=HelpTopics.objects.get(id = request.POST.get('help_type'))
        except:
            help_type:None  
        data = Recommendation.objects.create(title=request.POST.get('title'),
                                             description=request.POST.get('description'),
                                             user_type=request.POST.get('user_type'),
                                             created_by=request.user,
                                             help_type_id=help_type.id

                                             )
        if request.POST.get("category"):
            data.service=category
            data.save()
        messages.add_message(request, messages.INFO, 'Recommendation Added Successfully')
        return redirect("superuser:recommendation")


"""
Edit recommendations
"""
@login_required
def Edit_recommendation(request):        
    if request.method=="POST":
        if request.POST.get("category"):
            try:
                category = ServiceCategory.objects.get(id = request.POST.get("category"))
            except:
                category=None
        try:
            try:
                help_type=HelpTopics.objects.get(id = request.POST.get('help_type'))
            except:
                help_type:None  
            recommendation=Recommendation.objects.get(id=request.POST.get('recommendation_id'))
            if recommendation:
                if request.POST.get('title'):
                    recommendation.title=request.POST.get('title')
                if request.POST.get('description'):
                    recommendation.description=request.POST.get('description')
                if request.POST.get('user_type'):
                    recommendation.user_type=request.POST.get('user_type')
                if request.POST.get('category'):
                    recommendation.service = category
                if request.POST.get('help_type'):
                    recommendation.help_type_id=help_type.id
                recommendation.save()
                messages.add_message(request,messages.INFO,"Reccommendation Updated Successfully")
                return redirect("superuser:recommendation")
            return redirect("superuser:recommendation")
        except:
            recommendation=None


"""
Search recommendations
"""
@login_required
def Search_recommendation(request):
    if request.method == 'GET':
        search = request.GET.get("search")
        if not search:
            messages.error(request, 'Please enter somethings to search')
            return redirect('superuser:recommendation')
        elif request.GET.get("reset")=='reset':
            messages.error(request, 'Please enter somethings to search')
            return redirect('superuser:recommendation')
        if search:
            recommendation = Recommendation.objects.filter(title__icontains = search)
            return render(request, 'admin/recommendation.html',{'search':search,'nbar':'recommendation',"title":"Recommendation","search":request.POST.get("search"),"recommendation":recommendation,})

"""
Add Help topics
"""
@login_required
def Help_type(request):
    if request.method=="POST":
        data=HelpTopics.objects.create(title=request.POST.get('title'))
        messages.add_message(request,messages.INFO,"Help type added successfully")
        return redirect("superuser:view_help_type")

"""
Help Topics Display
"""
@login_required
def Help_type_view(request):
    topics=HelpTopics.objects.all().order_by("-created_on")
    return redirect('admin/recommendation.html',{"help_topics":topics})



"""
Assign Badge
"""
def AssignBadge(request):
    user = User.objects.get(id =request.POST.get('user_id'))
    if user:
        user.badge_id = request.POST.get('badge_input')
        user.save()
        messages.add_message(request, messages.INFO, 'Badge Assigned Successfully')
        return redirect('superuser:users_list')
    return redirect('superuser:users_list')

"""
Badge
"""
def Badges(request):
    badge=Badge.objects.all().order_by('-created_on')
    return render(request,"admin/add-badge.html",{'nbar':'badge',"title":"Add Badge","badges":badge})


"""
Add Badge
"""
def Add_badge(request):
    if request.method=="POST":
        if Badge.objects.filter(title=request.POST.get('title')):
            messages.add_message(request,messages.INFO,'Badge Already Added')
            return redirect('superuser:badge')
        Badge.objects.create(title=request.POST.get('title'),
                             image=request.FILES.get('image'))
        messages.add_message(request,messages.INFO,'Badge Added Successfully')
        return redirect('superuser:badge')

"""
Delete Badge
"""
def Delete_Badge(request):
    badge=Badge.objects.get(id=request.GET.get('id'))
    if badge:
        badge.delete()
        return redirect('superuser:badge')


"""
Edit Badge
"""
def Edit_Badge(request):
    badge=Badge.objects.get(id=request.POST.get('badge_id'))
    if badge:
        if request.POST.get('title'):
            badge.title=request.POST.get('title')
        if request.FILES.get('image'):
            badge.image=request.FILES.get('image')
        messages.add_message(request,messages.INFO,'Badge Updated Successfully')
        badge.save()
        return redirect('superuser:badge')



"""
Search Badge
"""
def Search_badge(request):
    if request.method=="GET":
        search = request.GET.get('search')
        if not search:
            messages.add_message(request,messages.INFO,'Please Type Something To Search')
            return redirect('superuser:badge')
        elif request.GET.get('reset')=='reset':
            messages.add_message(request,messages.INFO,'Please Type Something To Search')
            return redirect('superuser:badge')
        if search:
            badge=Badge.objects.filter(title__icontains=search)
            return render(request,"admin/add-badge.html",{"search":search,"title":"Add Badge","nbar":"badge","badges":badge})


@login_required
def PreviousBadgeData(request):
    if request.is_ajax():
        badge_id  = request.GET.get("badge_id")
        badge = Badge.objects.get(id=badge_id)
        if badge:
            data = {
                "id":badge.id,
                "title":badge.title,
            }
            return JsonResponse(data)

"""
Add Banners
"""
@login_required
def AddBanner(request):
    if request.method=='GET':
        banner = Banners.objects.all().order_by('-id')
        return render(request,"admin/banner.html",{'nbar':'Banner',"title":"Add Banner",'banner':banner})
    
    if request.method =="POST":
        if Banners.objects.filter(banner_title = request.POST.get("title")):
            messages.add_message(request, messages.INFO, 'Banner Title Already Exist')
            return redirect('superuser:add_banner')

        banners = Banners.objects.create(banner_title = request.POST.get("banner_title"),post_title = request.POST.get("post_title"),description = request.POST.get("description"))
        if request.FILES.get("image"):
            banners.image =request.FILES.get("image")
        banners.save()
        messages.add_message(request, messages.INFO, 'Banner Category Added Successfully')
        return redirect('superuser:add_banner')



"""
Delete Banner
"""
@login_required
def DeleteBanner(request):
    if request.method =="GET":
        banner = Banners.objects.get(id = request.GET.get("id"))
        if banner:
            banner.delete()
            messages.add_message(request, messages.INFO, 'Banner Deleted Successfully')
            return redirect('superuser:add_banner')


"""
Pervious details
"""
@login_required
def PreviousBannerData(request):
    if request.is_ajax():
        banner_id  = request.GET.get("banner_id")
        banner = Banners.objects.get(id=banner_id)
        if banner:
            data = {
                "id":banner.id,
                "banner_title":banner.banner_title,
                "post_title":banner.post_title,
                "description":banner.description,
            }
            return JsonResponse(data)


"""
edit banner
"""
@login_required
def EditBanner(request):
    if request.method == 'POST':
        banner =  Banners.objects.get(id=request.POST.get("banner_id"))
        if request.POST.get("banner_title",None):
            banner.title = request.POST.get("banner_title")
        
        if request.POST.get("post_title",None):
            banner.title = request.POST.get("banner_title")

        if request.POST.get("description",None):
            banner.description = request.POST.get("description")

        if request.FILES.get("image",None):
            banner.image = request.FILES.get("image")

        banner.save()
        messages.error(request, 'Banner Updated Successfully')
        return redirect('superuser:add_banner')


"""
Custom Request
"""
@login_required
def CustomRequest(request):
    custom_request= CustomService.objects.filter(created_by__role_id=USERS)
    return render(request,'admin/custom-request.html',{'nbar':'custom-request',"title":"Custom Request","custom_request":custom_request})



"""
Add Sub Admin
"""
@login_required
def SubAdmin(request):
    sub_admins =User.objects.filter(role_id = SUB_ADMIN).order_by('-id')
    return render(request,'admin/sub-admin.html',{'nbar':'sub-admin',"title":"Sub Admin","sub_admins":sub_admins})


"""
Add Service Categories
"""
@login_required
def AddSubAdmin(request):
    if request.method =="POST":
        try:
            User.objects.get(email=request.POST.get('email'))
            messages.add_message(request, messages.INFO, 'This email is already registered with other account')
            return redirect('superuser:sub_admin')
        except:
            user= User.objects.filter(role_id=4).count()
            if user>=5:
                messages.add_message(request, messages.INFO, 'You can only add five Sub Admins')
                return redirect('superuser:sub_admin')
            User.objects.create(
                email = request.POST.get('email'),
                password = make_password(request.POST.get('password')),
                role_id = SUB_ADMIN,
                is_superuser =1,
                is_staff =1,
                username=request.POST.get('email')
            )
            current_site = get_current_site(request)            
            context = {
                'domain':current_site.domain,
                'site_name': current_site.name,
                'protocol': 'https' if USE_HTTPS else 'http',
                'user_name':request.POST.get('email'),
                'password':request.POST.get('password')
            }
            subject = 'Activate account'
            message = render_to_string('user/activate_account.html', context)
            email_from = settings.EMAIL_HOST_USER
            email = request.POST.get('email')
            recipient_list = [email]
            email_message = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [email])
            html_email = render_to_string('user/activate_account.html',context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.send()
            messages.add_message(request, messages.INFO, 'Sub Admin added successfully, Link has been sent to User email to activate his/her account')
            return redirect('superuser:sub_admin')


"""
delete Sub-Admin
"""
@login_required
def DeleteSubAdmin(request):
    if request.method =="GET":
        try:
            user = User.objects.get(id = request.GET.get("id"))
            if user:
                user.delete()
                messages.add_message(request, messages.INFO, 'Sub Admin deleted successfully')
                return redirect('superuser:sub_admin')
        except:
            messages.add_message(request, messages.INFO, 'Sub Admin not found')
            return redirect('superuser:sub_admin')



"""
Pervious details
"""
@login_required
def PreviousSubAdminData(request):
    if request.is_ajax():
        user_id  = request.GET.get("user_id")
        user = User.objects.get(id=user_id)
        if user:
            data = {
                "id":user.id,
                "email":user.email,
            }
            return JsonResponse(data)

"""
edit Sub Admin
"""
@login_required
def SubAdminEdit(request):
    if request.method == 'POST':
        user =  User.objects.get(id=request.POST.get("user_id"))
        if request.POST.get("email",None):
            user.email = request.POST.get("email")
            user.username=request.POST.get('email')
        user.save()

        current_site = get_current_site(request)
        context = {
            'domain':current_site.domain,
            'site_name': current_site.name,
            'protocol': 'https' if USE_HTTPS else 'http',
        }
        message = render_to_string('admin/edit_subadmin_mail.html', context)
        mail_subject = 'SubAdmin Update'
        to_email = request.POST.get('email')
        email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
        html_email = render_to_string('admin/edit_subadmin_mail.html',context)
        email_message.attach_alternative(html_email, 'text/html')
        email_message.send()
    
        messages.error(request, 'Sub Admmin details updated successfully, link has been sent to User email to activate his/her account')
        return redirect('superuser:sub_admin')

"""
Task Management
"""
def TaxManagement(request):
    tax = Tax.objects.all().order_by('-id')
    return render(request,"admin/tax-management.html",{'nbar':'tax',"title":"Service Fee Percentage","tax":tax})


"""
Add Service Fee
"""
@login_required
def AddTaxPercentage(request):
    if request.method =="POST":
        tax = Tax.objects.create(tax_percentage = request.POST.get("tax_percent"), created_by = request.user )
        messages.add_message(request, messages.INFO, 'Service Fee Added Successfully')
        return redirect('superuser:tax_management')


"""
Pervious Tax details
"""
@login_required
def PreviousTaxPercent(request):
    if request.is_ajax():
        tax  = request.GET.get("tax_percent")
        tax_value = Tax.objects.get(id=tax)
        if tax_value:
            data = {
                "id":tax_value.id,
                "tax_percent":tax_value.tax_percentage,
                
            }
            return JsonResponse(data)


"""
Edit Service Fee
"""
@login_required
def EditTaxPercentage(request):
    if request.method == 'POST':

        tax_update =  Tax.objects.get(id=request.POST.get("tax_percent"))

        if request.POST.get("tax_percent",None):
            tax_update.tax_percentage = request.POST.get("tax_percentage")
        tax_update.save()
        messages.error(request, 'Service Fee Updated Successfully')
        return redirect('superuser:tax_management')


"""
Payment Release
"""
@login_required
def PaymentRelease(request):
    if request.method == 'POST':
       
        messages.error(request, 'Service Fee Updated Successfully')
        return redirect('superuser:tax_management')


"""
Payouts
"""
@login_required
def PayoutsManagement(request):
    payouts =Payouts.objects.all().order_by('-id')
    return render(request,'admin/payouts.html',{'nbar':'payouts',"title":"Payouts Management","payouts":payouts})


"""
Search Help request Admin Index
"""
def Search_help_admin(request):
    if request.GET.get('search1')=="":
        data={"created_by":[],"complain":[],"status":[],"image":[]}
        help=HelpRequest.objects.all().order_by('-created_on')[:4]
        for hl in help:
            data['created_by'].append(hl.created_by.first_name)
            data['complain'].append(hl.complain)
            data['status'].append(hl.status)
            data['image'].append(hl.created_by.profile_pic.url)
        return JsonResponse(data,safe=False)

    elif request.GET.get('search1'):
        data={"created_by":[],"complain":[],"status":[],"image":[]}
        help=HelpRequest.objects.filter(Q(created_by__first_name=request.GET.get('search1',None))|Q(complain__icontains=request.GET.get('search1',None)))
        for hl in help:
            data['created_by'].append(hl.created_by.first_name)
            data['complain'].append(hl.complain)
            data['status'].append(hl.status)
            data['image'].append(hl.created_by.profile_pic.url)
        return JsonResponse(data,safe=False)



        
def Sort_help_request(request):
    data={'name':[]}
    help=HelpRequest.objects.all().order_by('-created_by__first_name')
    for he in help:
        data['name'].append(he.created_by.first_name)
    return JsonResponse(data)

        
"""
Multiple Search custom  
"""
def Multiple_search_custom(request):
    if request.method=="GET":
        try:
            search=request.GET.get('title')
            d = {
                "title":request.GET.get('title'),
                "date":request.GET.get('date'),
                "is_appointment":request.GET.get('is_appointment')
            }
            syn = "SELECT * FROM tbl_custom_service WHERE "
            k =[]
            query = ""
            for i in d.keys():
                if i == 'is_appointment':    
                    if d[i]:
                        k.append(d[i])
                        query += i + " = %s and " 
                elif i == 'date':    
                    if d[i]:
                        k.append(d[i]+"%")
                        query += "DATE("+i+")" + " = %s and " 
                else:
                    if d[i]:
                        k.append('%'+d[i]+"%")
                        query += i + " LIKE %s and "
            query = query.rstrip(" and")
            syn += query
            searclist=[]
            for make in CustomService.objects.raw(syn,k):
                    searclist.append(make.id)
            custom_request = CustomService.objects.filter(id__in = searclist)
            if not custom_request:
                messages.add_message(request,messages.INFO, 'No Data Found')
            elif request.GET.get('reset')=='reset':
                return redirect("superuser:custom_requests")
            return render(request,'admin/custom-request.html',{'nbar':'custom-request',"title":"Custom Request","search":search,"custom_request":custom_request,"date":request.GET.get('date'),'is_appointment':request.GET.get('is_appointment')})
        except:
            return redirect("superuser:custom_requests")


"""
Muliple Search Appointments
"""
@login_required
def RvtSearch(request):
    if request.method=="GET":
        search = request.GET.get('search')
        if not search:
            messages.add_message(request,messages.INFO,'Please Type Something To Search')
            return redirect('superuser:rvt_users')
        elif request.GET.get('reset'):
            return redirect('superuser:rvt_users')
        if search:
            users=User.objects.filter(first_name__icontains=search,applied_for = RVT_LVT)
            return render(request,"admin/rvt-users-list.html",{"search":search,"title":"Rvt Applications","nbar" : "rvt_users","users":users})


"""
Search Appointments
"""
def Search_Appointments(request):
    if request.method == "GET":
        try:
            if request.GET.get('reset'):
                return redirect('superuser:appointment_management')
            appointments = Appointments.objects.all().order_by('-created_on')
            if request.GET.get("username"):
                appointments = appointments.filter(Q(created_for__email__icontains=request.GET.get("username"))|Q(created_by__email__icontains=request.GET.get("username"))|Q(created_for__full_name__icontains=request.GET.get("username"))|Q(created_by__full_name__icontains=request.GET.get("username"))|Q(created_for__username__icontains=request.GET.get("username"))|Q(created_by__address__icontains=request.GET.get("username"))|Q(created_for__address__icontains=request.GET.get("username")))
            if request.GET.get("date"):
                appointments = appointments.filter(date=request.GET.get("date"))
            if request.GET.get("status"):
                appointments = appointments.filter(status=request.GET.get("status"))
            if not appointments:
                messages.add_message(request, messages.INFO, 'No Data Found')
            return render(request, "admin/appointments.html", {"search":request.GET.get('username'),"appointments":appointments,"title":"Appointments", "nbar" : "appointment_management",'created_for__first_name':request.GET.get("username"),"date" :request.GET.get("date"),"status":request.GET.get("status")})
        except:
            messages.add_message(request, messages.INFO, 'Please Enter Something To Search')
            return redirect('superuser:appointment_management')


"""
Search Announcements
"""
def SearchAnnouncement(request):
    if request.method == "GET":
        try:
            search=request.GET.get('announcement')
            d = {'title':request.GET.get("announcement"),"status" :request.GET.get("status")}
            syn = "SELECT * FROM tbl_announcements WHERE "
            k =[]
            query = ""
            for i in d.keys():
                if d[i]:
                    k.append('%'+d[i]+"%")
                    query += i + " LIKE %s and "
                if i == 'status':    
                    if d[i]:
                        k.append(d[i])
                        query += i + " = %s and " 
                else:
                    pass
            query = query.rstrip(" and")
            syn += query
            searclist=[]
            for user in Announcements.objects.raw(syn,k):
                searclist.append(user.id)
            announcement = Announcements.objects.filter(id__in = searclist)
            if announcement:
                return render(request,'admin/announcements.html',{"search":search,"announcement":announcement,"title":"Announcements", "nbar" : "announcements","status" :request.GET.get("status")})
            elif request.GET.get('reset') == 'reset':
                    return redirect('superuser:announcement_list')
            else:
                messages.add_message(request, messages.INFO, 'No User Found')
                return render(request, "admin/announcements.html", {"search":search,"announcement":announcement,"title":"Announcements", "nbar" : "Announcements","status" :request.GET.get("status")})
        except:
            messages.add_message(request, messages.INFO, 'Please Enter Something To Search')
            return redirect('superuser:announcement_list')



"""
Search User
"""
def UserSearch(request):
    if request.method == "GET":
        users = User.objects.all().exclude(Q(role_id=ADMIN)|Q(role_id=SUB_ADMIN))
        badge = Badge.objects.all()
        if request.GET.get('user_name'):
            users = users.filter(Q(first_name__icontains = request.GET.get('user_name'))|Q(email__icontains = request.GET.get('user_name'))|Q(address__icontains = request.GET.get('user_name')))
        if request.GET.get("state_id"):
            users = users.filter(state_id = request.GET.get("state_id"))
        if request.GET.get('reset'):
            return redirect('superuser:users_list')
        else:
            if not users:
                messages.add_message(request, messages.INFO, 'No User Found')
            return render(request,'admin/users-list.html',{"search":request.GET.get('user_name'),"users":users,"title":"Users", "nbar" : "users_list",'first_name':request.GET.get("user_name"),"state_id" :request.GET.get("state_id"),"badge":badge})


"""
Payout Graph
"""
@login_required
def PaymentGraph(request):
    payments,credit,refund= [],[],[]
    months = {'jan':'1','feb':'2','mar':'3','apr':'4','may':'5','jun':'6','jul':'7','aug':'8','sep':'9','oct':'10','nov':'11','dec':'12'}
    for i in months.keys():
        x = Transactions.objects.filter(payment_type=PAYMENT,created_on__year=str(datetime.now().year),created_on__month= months[i]).values_list('amount',flat=True)
        total=0
        for i in x:
            total = total+float(i) 
        payments.append(round(total,2))
    for i in months.keys():
        x = Transactions.objects.filter(payment_type=CREDIT,created_on__year=str(datetime.now().year),created_on__month= months[i]).values_list('amount',flat=True)
        total=0
        for i in x:
            total = total+float(i)
        credit.append(round(total,2))
    for i in months.keys():
        x = Transactions.objects.filter(payment_type=REFUND,created_on__year=str(datetime.now().year),created_on__month= months[i]).values_list('amount',flat=True)
        total=0
        for i in x:
            total = total+float(i)
        refund.append(round(total,2))
    chart = {
        'chart': {'type': 'column'}, 
        'title': {'text': ""},
        'xAxis': { 'categories': [i.upper() for i in months.keys()]},
        'series': [{'name': 'Payments','data':payments},{"name":"Payout",'data':credit},{"name":"Refund","data":refund}]
    }
    return JsonResponse(chart)



"""
Job Opening
"""
def CareerJobOpening(request):
    job_openings=JobOpenings.objects.all().order_by('-id')
    return render(request,'admin/job-opening.html',{"title":"Job Openings","nbar" : "jop_opening","job_openings":job_openings})


"""
Add Job Openings
"""
@login_required
def AddJobOpenings(request):
    if request.method =="POST":
        if JobOpenings.objects.filter(job_title = request.POST.get("job_title")):
            messages.add_message(request, messages.INFO, 'Job Title Already Exist')
            return redirect('superuser:job_opening')
        JobOpenings.objects.create(job_title = request.POST.get("job_title"))
        messages.add_message(request, messages.INFO, 'Job Added Successfully')
        return redirect('superuser:job_opening')

"""
delete Job Openings
"""
@login_required
def DeleteJobOpening(request):
    if request.method =="GET":
        JobOpenings.objects.filter(id = request.GET.get("id")).delete()
        messages.add_message(request, messages.INFO, 'Job Deleted Successfully')
        return redirect('superuser:job_opening')

"""
Pervious Job details
"""
@login_required
def PreviousJobData(request):
    if request.is_ajax():
        job_id  = request.GET.get("id")
        job = JobOpenings.objects.get(id=job_id)
        if job:
            data = {
                "id":job.id,
                "title":job.job_title,
            }
            return JsonResponse(data)

"""
edit Job title
"""
@login_required
def JobTitleEdit(request):
    if request.method == 'POST':
        job =  JobOpenings.objects.get(id=request.POST.get("job_id"))
        if request.POST.get("title",None):
            job.job_title = request.POST.get("title")
        job.save()
        messages.error(request, 'Job Opening Updated Successfully')
        return redirect('superuser:job_opening')



"""
Job Applicant List
"""
@login_required
def JobApplicantList(request):
    applicant_list=Join_Us.objects.all().order_by('-id')
    try:
        page = request.GET.get('page', 1)
        paginator = Paginator(applicant_list, 10)
        try:
            applicant_list = paginator.page(page)
        except PageNotAnInteger:
            applicant_list = paginator.page(1)
    except EmptyPage:
        applicant_list = paginator.page(paginator.num_pages)

    except Exception as e:
        applicant_list = None
    return render(request,'admin/job-applicant.html',{"title":"Job Applicants","nbar" : "jop_applicant","applicant_list":applicant_list})
"""
Delete Applicant 
"""
@login_required
def DeleteApplicant(request):
    Join_Us.objects.filter(id=request.GET.get('id')).delete()
    return redirect('superuser:job_applicant_list')


"""
Search Applicants
"""
@login_required
def ApplicantsSearch(request):
    if request.method=="GET":
        search = request.GET.get('search')
        if not search:
            messages.add_message(request,messages.INFO,'Please Type Something To Search')
            return redirect('superuser:job_applicant_list')
        elif request.GET.get('reset')=='reset':
            messages.add_message(request,messages.INFO,'Please Type Something To Search')
            return redirect('superuser:job_applicant_list')
        if search:
            applicant_list=Join_Us.objects.filter(email__icontains=search)
            return render(request,"admin/job-applicant.html",{"search":search,"title":"Job Applicants","nbar" : "jop_applicant","applicant_list":applicant_list})


"""
Search Job Opening
"""
@login_required
def JobOpeningSearch(request):
    if request.method=="GET":
        search = request.GET.get('job_title')
        if not search:
            messages.add_message(request,messages.INFO,'Please Type Something To Search')
            return redirect('superuser:job_opening')
        elif request.GET.get('reset')=='reset':
            messages.add_message(request,messages.INFO,'Please Type Something To Search')
            return redirect('superuser:job_opening')
        if search:
            job_openings=JobOpenings.objects.filter(job_title__icontains=search)
            return render(request,"admin/job-opening.html",{"search":search,"title":"Job Openings","nbar" : "jop_opening","job_openings":job_openings})


"""
View Help Type
"""

@login_required
def View_help_type(request):
    help_type=HelpTopics.objects.all().order_by("-created_on")
    try:
        page = request.GET.get('page', 1)
        paginator = Paginator(help_type, 10)
        try:
            help_type = paginator.page(page)
        except PageNotAnInteger:
            help_type = paginator.page(1)
    except EmptyPage:
        help_type = paginator.page(paginator.num_pages)

    except Exception as e:
        help_type = None
    return render(request,"admin/help_type.html",{"nbar":"help_type","help_type":help_type,"title":"Help type"})


"""
Edit Help Type
"""
def Edit_help_type(request):
    if request.method=="POST":
        try:
            data = HelpTopics.objects.get(id=request.POST.get('help_id'))
            data.title=request.POST.get('help_title')
            data.save()
            messages.add_message(request,messages.INFO,'Help Type Updated Successfully!')
            return redirect('superuser:view_help_type')
        except:
            messages.add_message(request,messages.INFO,'Help Id Not Found')
            return redirect('superuser:view_help_type')

"""
Delete Help type
"""
def Delete_help_type(request):
    data = HelpTopics.objects.get(id=request.GET.get('id')).delete()
    return redirect('superuser:view_help_type')

@login_required
def PreviousHelpypeData(request):
    if request.is_ajax():
        help_id  = request.GET.get("help_id")
        help_id = HelpTopics.objects.get(id=help_id)
        if help_id:
            data = {
                "id":help_id.id,
                "title":help_id.title,
            }
            return JsonResponse(data)

        
"""
Search Help Type
"""
def Search_help_type(request):
    search = request.GET.get('search')
    if not search:
        messages.add_message(request,messages.INFO,"Please enter something to search")
        return redirect('superuser:view_help_type')
    elif request.GET.get('reset')=='reset':
        return redirect('superuser:view_help_type')
    help_type=HelpTopics.objects.filter(title__icontains=search)
    return render(request,"admin/help_type.html",{"nbar":"help_type","search":search,"help_type":help_type,"title":"Help type"})


"""
Print Appointments in PDF
"""
def AppointmentPDF(request):
    data=Appointments.objects.all()
    html_string = render_to_string('admin/pdf.html', {'appointments': data})
    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/mypdf.pdf');
    fs = FileSystemStorage('/tmp')
    with fs.open('mypdf.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="appointments.pdf"'
        return response


"""
Mileage Fees
"""
@login_required
def EditMileagePercentage(request):
    if request.method == 'POST':
        mileage_update =  Mileage.objects.get(id=request.POST.get("mileage_percent"))
        if request.POST.get("mileage_percent",None):
            mileage_update.mileage_percentage = request.POST.get("mileage_percentage")
        mileage_update.save()
        messages.error(request, 'Mielage Fee Updated Successfully')
        return redirect('superuser:mileage_management')


def MileageManagement(request):
    mileage = Mileage.objects.all().order_by('-id')
    return render(request,"admin/mileage-management.html",{'nbar':'mileage',"title":"Mileage Fee Percentage","mileage":mileage})

"""
Add Mileage Fee
"""
@login_required
def AddMileagePercentage(request):
    if request.method =="POST":
        mileage = Mileage.objects.create(mileage_percentage = request.POST.get("mileage_percent"), created_by = request.user )
        messages.add_message(request, messages.INFO, 'Mileage Fee Added Successfully')
        return redirect('superuser:mileage_management')


@login_required
def PreviousMileagePercent(request):
    if request.is_ajax():
        mileage  = request.GET.get("mileage_percent")
        mileage_value = Mileage.objects.get(id=mileage)
        if mileage_value:
            data = {
                "id":mileage_value.id,
                "mileage_percent":mileage_value.mileage_percentage,
                
            }
            return JsonResponse(data)

