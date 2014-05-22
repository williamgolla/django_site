from django.contrib import admin
from app.models import UserProfile, Event, Feedback, Comment

class UserAdmin(admin.ModelAdmin):
    fields = ['location']
    #list_display = ['username','password','email','join_date','last_online','location']

admin.site.register(UserProfile, UserAdmin)
admin.site.register(Event)
admin.site.register(Feedback)
admin.site.register(Comment)