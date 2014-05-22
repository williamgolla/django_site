from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from app.models import UserProfile
from app.helpers import all_info_one_profile, all_info_many_profiles

def user_info(request):
    ''' This makes the UserProfile data associated with request.user (if one exists)
    available in all contexts.
    '''
    
    try:
        profile = UserProfile.objects.get(user_id=request.user.id)
        myprofile = all_info_one_profile(profile)
        return {'myprofile': myprofile}        
    except:
        return {'myprofile': request.user}