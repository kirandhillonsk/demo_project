from django.db import models

from superuser.models import JobOpenings

# Create your models here.
class Join_Us(models.Model):
    name=models.CharField(max_length=100,null=True,blank=True)
    Job_type =models.ForeignKey(JobOpenings,on_delete=models.CASCADE,null=True, blank=True)
    email=models.EmailField('email',null=True,blank=True)
    mobile=models.CharField(max_length=100,null=True,blank=True)
    resume = models.FileField(upload_to='resume',blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    class Meta:
        managed=True
        db_table='tbl_join_us'