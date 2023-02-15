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
from unicodedata import category
import environ
from rest_framework import serializers as Serializers
from rest_framework_jwt import serializers
from api.serializer import UserSerializer
from enduser.serializer import PetSerializer
from rvt_lvt.models import *
from superuser.models import Announcements, Banners, Recommendation

env = environ.Env()
environ.Env.read_env()


"""
Banner 
"""
class BannerSerializer(Serializers.ModelSerializer):
    class Meta:
        model = Announcements
        fields = '__all__'
