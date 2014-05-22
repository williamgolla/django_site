from django.conf.urls import patterns, url

from app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'), 
    
    url(r'^user/(?P<user_id>\d+)/$', views.user_detail, name='user_detail'),
    
    url(r'^users/$', views.users, name='users'),
    url(r'^users/n=(?P<nameQuery>.+?)/l=(?P<locQuery>.+?)/$', views.users_search, name='users_search'),
    url(r'^users/n=(?P<nameQuery>.+?)/$', views.users_name_search, name = 'users_name_search'),
    url(r'^users/l=(?P<locQuery>.+?)/$', views.users_loc_search, name = 'users_loc_search'),
    
    url(r'^events/$', views.events, name='events'),
    url(r'^events/n=(?P<nameQuery>.+?)/l=(?P<locQuery>.+?)/$', views.events_search, name='events_search'),
    url(r'^events/n=(?P<nameQuery>.+?)/$', views.events_name_search, name = 'events_name_search'),
    url(r'^events/l=(?P<locQuery>.+?)/$', views.events_loc_search, name = 'events_loc_search'),
    
    url(r'^event/new/$', views.new_event, name='new_event'), 
    url(r'^event/(?P<event_id>\d+)/$', views.event_detail, name='event_detail'),
    url(r'^event/edit/$', views.edit_event, name='edit_event'),
    url(r'^event/join/$', views.join_event, name='join_event'),
    url(r'^event/leave/$', views.leave_event, name='leave_event'),
    url(r'^event/delete/$', views.delete_event, name='delete_event'), 
    url(r'^event/promote/$', views.promote, name='promote'),  
    url(r'^event/demote/$', views.demote, name='demote'),  
    url(r'^event/kick/$', views.kick, name='kick'), 
    
    url(r'^feedback/(?P<event_id>\d+)/$', views.feedback, name='feedback'),

    url(r'^settings/$', views.edit_user, name='settings'),

    url(r'^event/(?P<event_id>\d+)/$', views.comment, name='comment'),
    url(r'^edit_comment/(?P<comment_id>\d+)/$', views.edit_comment, name='edit_comment'),
    url(r'^event/delete_comment/$', views.delete_comment, name='delete_comment')
    
)
