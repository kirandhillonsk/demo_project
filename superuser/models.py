from statistics import mode
from django.db import models
from accounts.constants import ANNOUNCEMENT_STATUS, USER_TYPE
from accounts.models import User
from contact.models import ContactUs
from rvt_lvt.models import ServiceCategory, Services

class NewsletterSubscription(models.Model):
    email = models.CharField( max_length=100,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    price = models.TextField(max_length=50,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'tbl_Newsletter_Subscription'



class MailRevert(models.Model):
    title=models.CharField(max_length=100,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    attachment=models.FileField(upload_to='Email_message',null=True,blank=True)
    created_for=models.ForeignKey(ContactUs,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table='tbl_mail_revert'



"""
Help Topics
"""
class HelpTopics(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    
    class Meta:
        managed = True
        db_table = 'tbl_help_topics' 
        
"""
Recommendation 
"""
class Recommendation(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(null=True,blank=True)
    service = models.ForeignKey(ServiceCategory,on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.PositiveIntegerField(blank=True,null=True,choices=USER_TYPE)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    help_type = models.ForeignKey(HelpTopics,on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'tbl_recommendation' 



"""
Banner 
"""
class Banners(models.Model):
    banner_title = models.CharField(max_length=255,blank=True,null=True)
    post_title = models.CharField(max_length=255,blank=True,null=True)
    description = models.TextField(null=True,blank=True)
    image=models.FileField(upload_to='banner_image',null=True,blank=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    class Meta:
        managed = True
        db_table = 'tbl_banner' 


"""
Announcements
"""
class Announcements(models.Model):
    title = models.CharField(max_length=255,blank=True,null=True)
    image = models.ImageField(upload_to='announcements')
    description = models.TextField(blank=True,null=True)
    status = models.BooleanField(default=0)
    target = models.CharField(max_length=10,choices=ANNOUNCEMENT_STATUS)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'tbl_announcements'


"""
Tax
"""
class Tax(models.Model):
    tax_percentage = models.CharField(max_length=5,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    class Meta:
        managed = True
        db_table = 'tbl_tax'

"""
Mileage
"""
class Mileage(models.Model):
    mileage_percentage = models.CharField(max_length=5,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    class Meta:
        managed = True
        db_table = 'tbl_mileage'


"""
Revenue
"""
class Revenue(models.Model):
    amount=models.IntegerField(null=True,blank=True)
    created_on=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    class Meta:
        managed = True
        db_table = 'tbl_revenue'


"""
Job Openings
"""
class JobOpenings(models.Model):
    job_title=models.CharField(max_length=255,blank=True,null=True)
    created_on=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    class Meta:
        managed = True
        db_table = 'tbl_job_openings'