'''
/**
 *@copyright : ToXSL Technologies Pvt. Ltd. < www.toxsl.com >
 *@author     : Shiv Charan  spaceeta < shiv@toxsl.com >
 *
 * All Rights Reserved.
 * Proprietary and confidential :  All information contained herein is, and remains
 * the property of ToXSL Technologies Pvt. Ltd. and its partners.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 *
 *
 */
'''
import os
import environ
from urllib.request import urlopen
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import stripe
import mimetypes
from django.views import View
from accounts.models import User
from enduser.models import PetType
from wsgiref.util import FileWrapper
from django.views.generic import View
from accounts.forms import SubscriptionForm
from enduser.constants import NORMAL_SERVICE
from django.shortcuts import render,redirect
from accounts.constants import *
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.http.response import StreamingHttpResponse
from frontend.models import Join_Us
from page.models import Page
from rating.models import Rating
from rvt_lvt.models import CustomService, ServiceCategory, Services
from django.contrib import messages
from django.db.models import Q
from superuser.models import JobOpenings
from django.urls import reverse_lazy

env = environ.Env()
environ.Env.read_env()
stripe.api_key = env('STRIPE_KEY')


"""
forntend Index Page
"""
def index(request):
    API_KEY = env('GOOGLE_API_KEY')
    try:
        user = User.objects.get(id=request.user.id)
        if not request.user.customer_id or request.user.customer_id==None:
            try:
                stripe_customer = stripe.Customer.create(
                    description = " space User - %s " % user.email,
                    email = user.email
                )
                user.customer_id = stripe_customer.id
                user.is_verify_mail = True
                user.save()
            except Exception as e:
                pass
    except:
        pass
    try:
        user = User.objects.get(id=request.user.id)
        img_temp = NamedTemporaryFile(delete = True)
        img_temp.write(urlopen(request.user.socialaccount_set.filter(provider='google')[0].extra_data['picture']).read())
        img_temp.flush()
        user.profile_pic.save("image_%s" % user.pk, File(img_temp))
    except:
        pass
    pet_type = PetType.objects.filter(service_type=NORMAL_SERVICE)
    services = ServiceCategory.objects.all().order_by('-id')
    if request.user.is_authenticated and request.user.is_superuser and request.user.role_id == 1:
        return redirect('admin:index')
    elif request.user.is_authenticated and request.user.is_superuser and request.user.role_id == 4:
        return redirect('admin:index')
    elif request.user.is_authenticated and request.user.role_id == RVT_LVT:
        if request.user.state_id == ACTIVE:
            return redirect('rvt_lvt:rvt_dashboard')
        elif request.user.state_id == INACTIVE:
            messages.add_message(request, messages.INFO, 'Your account has been deactivated. Please contact admin to activate your account.')
            return redirect('accounts:web_login')
        elif request.user.state_id == DELETED:
            messages.add_message(request, messages.INFO, 'Your account has been deleted. Please create a new one.')
            return redirect('accounts:web_login') 
    elif request.user.is_authenticated and request.user.role_id == USERS:
        if request.user.state_id == ACTIVE:
            return redirect('enduser:user_dashboard')
        elif request.user.state_id == INACTIVE:
            messages.add_message(request, messages.INFO, 'Your account has been deactivated. Please contact admin to activate your account.')
            return redirect('accounts:web_login')
        elif request.user.state_id == DELETED:
            messages.add_message(request, messages.INFO, 'Your account has been deleted. Please create a new one.')
            return redirect('accounts:web_login')
    else:
        rating = Rating.objects.all().order_by('-rating')[:5]
        return render(request, "frontend/index.html", {"pet_type":pet_type,"services":services,"API_KEY":API_KEY,"rating":rating})


def error_404(request, exception):
    data = {}
    return render(request,'errorpages/404.html', data)
    

def error_500(request):
    data = {}
    return render(request,'errorpages/500.html', data)


"""
Robots File
"""
def robot(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path= os.path.join(BASE_DIR)
    fin = open(f'{path}/project/robots.txt', 'rb')
    file_content = fin.read()
    fin.close()
    return HttpResponse(file_content, content_type="text/plain")

  
# contact us static page
def ContactUs(request):
    return render(request,'frontend/contact-us.html',)


"""
Find service static page
"""
def FindServices(request):
    API_KEY=env('GOOGLE_API_KEY')
    lattitude = request.GET.get("latitude")
    longitude = request.GET.get("longitude")
    services_list =ServiceCategory.objects.all().order_by('-id')
    if lattitude and longitude and lattitude!= 'None' and  longitude!= 'None':
        q=''
        user_list = []
        for i in User.objects.raw('''
                    SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                    cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                    sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id=1 Having  distance < {3};  
                    '''.format(lattitude,longitude,q,env('MILES_RADIUS'))):
            user = User.objects.get(id=i.id)
            if str(user.is_verified) == str(VERIFIED):
                user_list.append(i.id)
        rvt_users = User.objects.filter(id__in=user_list)
    else:
        rvt_users = User.objects.filter(is_verified=VERIFIED)

    if request.GET.get("service"):
        service = Services.objects.filter(category__id = request.GET.get("service"),is_active=True).values_list("created_by_id",flat=True)
        rvt_users = rvt_users.filter(id__in = service) 

    if request.GET.get("pet"):
        service = Services.objects.filter(pet_id = request.GET.get("pet"),is_active=True).values_list("created_by_id",flat=True)
        rvt_users = rvt_users.filter(id__in = service)   

    if request.GET.get('search_service'):
        service_cat = ServiceCategory.objects.filter(title__icontains = request.GET.get('search_service')).values_list("id",flat=True)
        custom = CustomService.objects.filter(title__icontains = request.GET.get("search_service"),is_active=True).values_list("created_by_id",flat=True) 
        service = Services.objects.filter(category_id__in = service_cat,is_active=True).values_list("created_by_id",flat=True)
        rvt_users = rvt_users.filter(Q(id__in = service)|Q(id__in = custom))  

    if request.GET.get('search_service_select'):
        service_cat = ServiceCategory.objects.filter(title = request.GET.get('search_service_select')).values_list("id",flat=True)
        service = Services.objects.filter(category_id__in = service_cat,is_active=True).values_list("created_by_id",flat=True)
        rvt_users = rvt_users.filter(id__in = service)    

    if request.GET.get('city'):
        rvt_users = rvt_users.filter(city = request.GET.get('city')) 

    if request.GET.get('state'):
        rvt_users = rvt_users.filter(state = request.GET.get('state')) 

    if request.GET.get('country'):
        rvt_users = rvt_users.filter(country = request.GET.get('country')) 

    user_list = Services.objects.all().values_list('created_by_id',flat=True)
    user_list_custom = CustomService.objects.all().values_list('created_by_id',flat=True)
    rvt_users = rvt_users.filter(Q(id__in=user_list)|Q(id__in=user_list_custom))
    servicess = []
    for user in User.objects.filter(is_verified=VERIFIED):
        try:        
            min_price_service = Services.objects.filter(created_by = user).order_by('price')[0]
        except:
            min_price_service = None
        try:        
            min_price_custom = CustomService.objects.filter(created_by = user).order_by('price')[0]
        except:
            min_price_custom = None
        
        if min_price_service and min_price_custom:
            if float(min_price_service.price if min_price_service.price else 0) < float(min_price_custom.price if min_price_custom.price else 0):
                servicess.append(min_price_service)
            else:
                servicess.append(min_price_custom)
        elif min_price_custom:
            servicess.append(min_price_custom)
        elif min_price_service:
            servicess.append(min_price_service)
    return render(request,'frontend/find-services.html',{"map_rvt":servicess,"rvt_user":rvt_users,"services_list":services_list,"search_service":request.GET.get('search_service'),"selected_city":request.GET.get('city'),"selected_country":request.GET.get('country'),"selected_state":request.GET.get('state'),"search_service_select":request.GET.get('search_service_select'),"select_service":int(request.GET.get("service")) if request.GET.get("service") else "","API_KEY":API_KEY,"latitude":lattitude,"longitude":longitude,"address":request.GET.get('address')})


"""
Service list
"""
def ServiceList(request):
    service = Services.objects.filter(created_by_id = request.GET.get('user_id'),is_active=True)
    custom = CustomService.objects.filter(created_by_id = request.GET.get('user_id'),is_active=True)
    try:        
        min_price = Services.objects.filter(created_by_id = request.GET.get('user_id'),is_active=True).order_by('price')[0]
    except:
        min_price = None

    data = {"id":None, "services" :[],"image":[],'price':[],'pets':[]}
    data['price'] = min_price.price if min_price else 0
    data["services"].clear()
    for services in service:
        data["id"] = services.created_by.id
        if services.category.title not in data["services"]:
            data["services"].append(services.category.title)
            data["pets"].append(services.pet.name)
            if services.category.image:
                data["image"].append(services.category.image.url)
            else:
                data["image"].append("")
        else:
            data["pets"][len(data["pets"])-1] = data["pets"][len(data["pets"])-1]+","+services.pet.name
    for cust in custom:
        if cust.title not in  data["services"]:
            data["id"] = request.GET.get('user_id')
            data["services"].append(cust.title)
            data["pets"].append(cust.pet_type.name)
            if cust.image:
                data["image"].append(cust.image.url)
            else:
                data["image"].append("")
    return JsonResponse(data)


# about us static page
def Career(request):
    form = SubscriptionForm()
    job_openings = JobOpenings.objects.all().order_by('-id')
    return render(request,'frontend/career.html',{"form":form,"job_openings":job_openings})

# career static page
def HelpSupport(request):
    return render(request,'frontend/help-support.html')


# Profile page
def ProfileView(request):
    price = []
    try:        
        min_price_service = Services.objects.filter(created_by_id = request.GET.get('id')).order_by('price')[0]
    except:
        min_price_service = None
    try:        
        min_price_custom = CustomService.objects.filter(created_by_id = request.GET.get('id')).order_by('price')[0]
    except:
        min_price_custom = None
    
    if min_price_service and min_price_custom:
        if float(min_price_service.price if min_price_service.price else 0) < float(min_price_custom.price if min_price_custom.price else 0):
            min_price = min_price_service.price
        else:
            min_price = min_price_custom.price
    elif min_price_custom:
        min_price = min_price_custom.price
    elif min_price_service:
        min_price = min_price_service.price
    else:
        min_price = 0

    rvt_user = User.objects.get(id = request.GET.get('id'))
    service = Services.objects.filter(created_by_id = rvt_user.id,is_active=True)
    custom = CustomService.objects.filter(created_by_id = rvt_user.id,is_active=True)
    data = {"id":None, "services" :[]}
    servicess,images,price,pets = [],[],[],[]
    data["services"].clear()
    for services in service:
        servicess.append(services.category.title)
        price.append(services.price)
        if services.category.image:
            images.append(services.category.image.url)
        else:
            images.append("")
        pets.append(services.pet.name)

    for cust in custom:
        servicess.append(cust.title)
        price.append(cust.price)
        if cust.image:
            images.append(cust.image.url)
        else:
            images.append("")
        pets.append(cust.pet_type.name)    
    servicess = zip(servicess, images,price,pets)

    rvt_detailed_services = Services.objects.filter(created_by_id = rvt_user.id,is_active=True)

    ### Get Unique Services
    rvt_detailed_services_unique = []
    covered_services = []
    for rvt_detailed_service in rvt_detailed_services:
        srv = {}
        srv["category"] = rvt_detailed_service.category
        srv["pet"] = rvt_detailed_service.pet
        if rvt_detailed_service.category.title not in covered_services:
            covered_services.append(rvt_detailed_service.category.title)
            rvt_detailed_services_unique.append(srv)
   
    #######################

    rvt_detailed_custom_services = CustomService.objects.filter(created_by_id = rvt_user.id,is_active=True)
    rating = Rating.objects.filter(created_for=rvt_user).order_by('-rating')[:5]
    next_page=reverse_lazy("enduser:user_rvt_profile", kwargs={'id': rvt_user.id })
    next_chat_page=reverse_lazy("chat:user_chat")
    return render(request,'frontend/profile.html',{"user":rvt_user, "rvt_detailed_services":rvt_detailed_services, "rating":rating,"min_price":min_price, "rvt_detailed_custom_services":rvt_detailed_custom_services, "rvt_detailed_services_unique":rvt_detailed_services_unique, "next_page": next_page, "next_chat_page":next_chat_page})


# wrapper for byte range of transceiver for browsers 
class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


"""       
search service
"""
def SearchService(request):
    API_KEY=env('GOOGLE_API_KEY')
    search = request.GET.get("search_service")
    if search:
        service_cat = ServiceCategory.objects.filter(title__icontains = search).values_list("id",flat=True)
        service = Services.objects.filter(category_id__in = service_cat).values_list("created_by_id",flat=True)
        user_list = []
        nearby_user = []
        rvt_users = User.objects.filter(id__in = service)
        for rvt in rvt_users:
            user_list.append(rvt.id)
        q=''
        for i in User.objects.raw('''
                SELECT id, ( 6367 * acos( cos( radians( {0} ) ) * cos( radians(latitude) ) * 
                cos( radians(longitude) - radians( {1} ) ) + sin( radians( {0} ) ) * 
                sin( radians(latitude) ) ) ) AS distance FROM tbl_user{2} WHERE state_id = 1 Having  distance < {3};  
                '''.format('30.7333','76.7794',q,env('MILES_RADIUS'))):
            user = User.objects.get(id=i.id)
            if str(user.is_verified) == str(VERIFIED):
                nearby_user.append(i.id)
        final_user_list = [value for value in user_list if value in nearby_user] 
        user = User.objects.filter(id__in = final_user_list)
        return render(request,'frontend/find-services.html',{"rvt_user":user,"search":request.GET.get("search_service"),"API_KEY":API_KEY})
    return render(request,'frontend/find-services.html',{"API_KEY":API_KEY})



"""       
User check RVT
"""
def UserCheckRvt(request):
    data = {"is_user" :'false'}
    user = User.objects.filter(Q(is_verified = UNVERIFIED)|Q(is_verified = DECLINED),id=request.GET.get('user_id'))
    if user:
        data["is_user"] = "true"
    return JsonResponse(data)


def TermPage(request):
    try:
        page = Page.objects.get(type_id = TERMS_AND_CONDITION)
    except:
        page = None
    return render(request, 'frontend/terms-and-conditions.html',{"page":page})


def PrivacyPage(request):
    try:
        page = Page.objects.get(type_id = PRIVACY_POLICY)
    except:
        page = None
    return render(request, 'frontend/privacy-policy.html',{"page":page})


def CookiePolicyPage(request):
    try:
        page = Page.objects.get(type_id = COOKIE_POLICY)
    except:
        page = None
    return render(request, 'frontend/cookie-policy.html',{"page":page})


def AboutPage(request):
    return render(request, 'frontend/about.html')


"""
Join us carrier
"""
def join_us(request):
    Join_Us.objects.create(
        name=request.POST.get('name'),
        email=request.POST.get('email'),
        mobile=request.POST.get("mobile_number"),
        resume=request.FILES.get('upload_resume'),
        Job_type_id=request.POST.get('job_type')
        )
    messages.add_message(request, messages.INFO, 'Your Application Registered Successfully')
    return redirect('frontend:career')
    
        
def handler404(request, exception, template_name="frontend/404.html"):
    return render(request, template_name, status=404)
    

def handler500(request, *args, **argv):
    return render(request, 'frontend/500.html', status=500)
    

def handler403(request, exception, template_name="frontend/404.html"):
    return render(request, template_name, status=403)
    

def handler400(request, exception, template_name="frontend/404.html"):
    return render(request, template_name, status=400)

# Additional Helper Functions
##################################################################
def get_rvt_banner_services(rvt_user):
    services = Services.objects.filter(created_by_id = rvt_user.id)
    included_services  = []
    new_services = []
    for service in services:
        if service.category.title not in included_services:
            new_services.append(service)
            included_services.append(service.category.title)
    return new_services

def get_rvt_detailed_services(rvt_user):
    services = Services.objects.filter(created_by_id = rvt_user.id)
    return services