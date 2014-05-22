from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory

from app.models import UserProfile, Event, Feedback, Comment
from app.forms import UserForm, UserProfileForm, EditUserForm, EventForm, EditEventForm, FeedbackForm, CommentForm, EditCommentForm
from app.helpers import all_info_one_profile, all_info_many_profiles, auto_msg, auto_msg_all, errors, get_rep, make_friends
from django_messages.models import Message

from datetime import datetime, timedelta
import json

### Registration, Login, and Logout

def index(request):
    ''' If logged in, direct to logged in user's profile page. Otherwise this is a login and registration form.
    '''
    
    # Redirect to user page if already logged in
    if request.user.is_authenticated():
        user = UserProfile.objects.get(user_id=request.user.id)
        return HttpResponseRedirect('/user/%d' % user.id)
    
    # Otherwise this is a registration page    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            login(request, user)
            user = UserProfile.objects.get(user_id=user.id)
            return HttpResponseRedirect('/user/%d' % user.id)
        else:
            print user_form.errors, profile_form.errors  
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'app/index.html', context)    

def user_login(request):
    ''' Log the user in if they can authenticate.
    '''
    
    context = RequestContext(request)
    data = {}

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                user = UserProfile.objects.get(user_id=user.id)
                data['redirect'] = '/user/%d' % user.id
            else:
                data['error'] = "Your account is disabled."
        else:
            data['error'] = "Invalid login details supplied."
        
    return HttpResponse(json.dumps(data), content_type="application/json") 

@login_required
def user_logout(request):
    ''' Log the user out.
    We don't need to explictly check the user is logged in because of the decorator above.
    '''
    
    logout(request)

    return HttpResponseRedirect('/')

### User related views ###

@login_required
def users(request):
    ''' Get and return a list of all UserProfiles, listed in the order they signed up.
    '''
    
    profiles = UserProfile.objects.all()        
    users = all_info_many_profiles(profiles)
    
    context = {'users': users}
    
    return render(request, 'app/users.html', context)

@login_required
def user_detail(request, user_id):
    ''' Get and return all details for the UserProfile with user_id = user_id.
    '''
    
    profile = get_object_or_404(UserProfile, pk=user_id)
       
    events_created = Event.objects.filter(created_by=user_id)
    events_participated = profile.events.all()
    feedback_by = profile.feedback_by.all()
    feedback_for = profile.feedback_for.all()
    profile = all_info_one_profile(profile)
    rep = get_rep(feedback_for)
    friend_ids = make_friends(feedback_by, feedback_for)
    friends = []
    for user in friend_ids:
        friend = get_object_or_404(UserProfile, pk=user)
        friend = all_info_one_profile(friend)
        friends.append(friend)
    
    context = {'profile': profile, 'events_created': events_created, 'events_participated': events_participated,
               'feedback_by': feedback_by, 'rep': rep, 'friends': friends}
    
    return render(request, 'app/user_detail.html', context)

@login_required
def edit_user(request):
    '''
    '''

    data = {}
    
    if request.method == "POST":
        form = EditUserForm(request.POST)
        if form.is_valid():
            changes = form.cleaned_data
            profile = UserProfile.objects.get(user_id=request.user.id)
            user = authenticate(username=profile.user.username, password=changes['current_password'])
            if user is not None:
                if changes['new_password'] != '':
                    profile.user.set_password(changes['new_password'])
                    profile.user.save()
                if changes['email'] != '':
                    profile.user.email = changes['email']
                    profile.user.save()
                if changes['location']:
                    profile.location = changes['location']
                    profile.save()
                return HttpResponseRedirect('/user/%d' % profile.id)
            else:
                data = errors('Invalid password Supplied', data)
                return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        form = EditUserForm()

    return render(request, 'app/settings.html', {'form': form})
                

### User Searching ###

@login_required
def users_name_search(request, nameQuery):
    '''
    '''

    return users_search(request, nameQuery, '')

@login_required
def users_loc_search(request, locQuery):
    '''
    '''

    return users_search(request, '', locQuery)

@login_required
def users_search(request, nameQuery, locQuery):
    ''' Get and return a list of all UserProfiles with name like nameQuery and location like locQuery, listed in the order they signed up.
        If locQuery is the empty string, returns the result of users(request).
    '''

    profiles = UserProfile.objects.filter(location__contains=locQuery, user__username__contains=nameQuery)
    users = all_info_many_profiles(profiles)
    loc = locQuery
    name = nameQuery
    
    context = {'users': users, 'location': loc, 'name': name}
    
    return render(request, 'app/search_users.html', context)

### Event related views ###

@login_required
@csrf_exempt
def events(request):
    ''' Get and return a list of all Events, separating them into events that are in_progress,
    upcoming, or have already ended.
    '''
    
    now = timezone.now()
    msg = None
    
    if request.method == 'POST':
        if request.POST.get('msg', '') == 'deleted':
            msg = ('deleted')       

    in_progress = Event.objects.filter(event_time__lte=now, end_time__gte=now)
    upcoming = Event.objects.filter(event_time__gt=now)
    past = Event.objects.filter(end_time__lte=now)
        
    context = {'in_progress': in_progress, 'upcoming': upcoming, 'past': past, 'msg': msg}
    return render(request, 'app/events.html', context)

@login_required
def event_detail(request, event_id):
    ''' Get and return all details for the Event with event_id = event_id.
    '''
    
    now = timezone.now()
    
    event = get_object_or_404(Event, id=event_id)    
    profile = UserProfile.objects.get(user_id=request.user.id)
    
    participants = all_info_many_profiles(event.participants.all())    
    owners = all_info_many_profiles(event.owners.all())
    comments = Comment.objects.filter(event=event_id)
    
    editform = EditEventForm(instance=event)   
    event_over = event.end_time <= now
    in_progress = event.event_time <= now and now <= event.end_time
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            note = comment_form.save(commit=False)
            note.author = profile
            note.event = event
            note.created = now
            note.save()
            return HttpResponseRedirect('/event/%d' % event.id)
    else:
        comment_form = CommentForm()
        
    context = {'event': event, 'participants': participants, 'owners': owners, 
               'editform': editform, 'comments': comments, 'comment_form': comment_form,
               'event_over': event_over, 'in_progress': in_progress}
    
    return render(request, 'app/event_detail.html', context)

@login_required
def new_event(request):
    ''' Create a new Event.
    Error if any of the fields are blank.
    Error if event_time and end_time aren't valid timestamps.
    Error if end_time <= event_time.
    '''
    
    context = RequestContext(request)
    profile = UserProfile.objects.get(user_id=request.user.id)  
    
    if request.method == 'POST':
        form = EventForm(request.POST)

        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = profile
            note.save()
            note.owners.add(profile)
            note.save()
            profile.events.add(Event.objects.get(id=note.id))
            profile.save()
            return index(request)
        else:
            print form.errors
    else:
        form = EventForm()
        
    return render_to_response('app/new_event.html', {'form': form}, context)

@login_required
def edit_event(request):
    ''' Edit an Event
    '''
    
    now = timezone.now()
    profile = UserProfile.objects.get(user_id=request.user.id)
    data = {}
    
    if request.method == 'POST':
        event_id = request.POST['event_id']
        event = get_object_or_404(Event, id=event_id)
        form = EditEventForm(request.POST)
        
        if event.end_time <= now:
            data["error"] = "Cannot edit Event that has already ended."
            return HttpResponse(json.dumps(data), content_type="application/json")  

        if form.is_valid():
            changes = form.cleaned_data
            user = authenticate(username=profile.user.username, password=changes['password'])
            if user is not None:
                event.name = changes['name']
                event.description = changes['description']
                event.location = changes['location']
                event.event_time = changes['event_time']
                event.end_time = changes['end_time']
                event.save()
                data["success"] = "success"
            else:
                data['password'] = "Incorrect Password"
        else:
            data = form.errors
            return HttpResponse(json.dumps(data))
        
    return HttpResponse(json.dumps(data), content_type="application/json")  

@login_required
def join_event(request):
    ''' Join an Event that has already been created. 
    Error if you attempt to join an Event you are already part of.
    '''
    
    now = timezone.now()
    data = {}  
    
    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST['event_id']
        
        profile = UserProfile.objects.get(user_id=request.user.id)
        event = get_object_or_404(Event, id=event_id)   
           
        if event.end_time <= now:
            data = errors("Cannot join event. This event has ended.", data)
        if profile in event.participants.all():
            data = errors("Cannot join event. You are already a participant.", data)
                
        if 'error' not in data:
            event.participants.add(profile)
            event.save()
            
            subject = "%s has joined your event" % all_info_one_profile(profile)['username']
            body = "%s has joined your event" % all_info_one_profile(profile)['username']
            auto_msg_all(event.owners.all(), subject, body)
            
            if event.event_time <= now:
                data['success'] = "Successfully joined event. Please note that this event has already started"
            else:
                data['success'] = "Successfully joined event."           
        
    return HttpResponse(json.dumps(data), content_type="application/json")    

@login_required
def leave_event(request):
    ''' Leave an Event that you have joined or created. 
    Error if you attempt to leave an Event you are not part of.
    Error if you attempt to leave an Event without first making someone else owner.
    '''    

    now = timezone.now()
    data = {}

    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST['event_id']
        
        profile = UserProfile.objects.get(user_id=request.user.id)
        event = get_object_or_404(Event, id=event_id) 
        event_over = event.end_time <= now
        
        if event_over:
            data = errors("Cannot leave event. This event has ended.", data)
        if profile not in event.participants.all():
            data = errors("Cannot leave event. You are not in the event.", data)            
        if profile in event.owners.all() and event.owners.count() == 1 and not event_over:
            data = errors("Cannot leave event. Please make someone else an owner before leaving.", data)
        
        if 'error' not in data:
            if profile in event.owners.all():
                event.owners.remove(profile)             
            event.participants.remove(profile)
            event.save()
            
            subject = "%s has left your event" % all_info_one_profile(profile)['username']
            body = "%s has left your event" % all_info_one_profile(profile)['username']
            auto_msg_all(event.owners.all(), subject, body)    
            
            data["success"] = "Successfully left event."     
    
    return HttpResponse(json.dumps(data), content_type="application/json") 
  
@login_required  
def delete_event(request):
    ''' Delete an Event that you have joined or created. 
    Error if the requestor is not an owner.
    '''  
    
    now = timezone.now()
    data = {}
    
    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST['event_id']
        
        event = get_object_or_404(Event, id=event_id)
        requestor = UserProfile.objects.get(user_id=request.user.id)
    
        if requestor not in event.owners.all():
            data = errors("You do not have permission to perform this event.", data)
        if event.end_time <= now:
            data = errors("Cannot delete event. This event has ended.", data)
        if event.event_time <= now and now <= event.end_time:
            data = errors("Cannot delete event. This event is currently in progress.", data)
        
        if 'error' not in data:
            subject = "%s has been deleted" % event.name
            body = "%s has been deleted" % event.name          
            auto_msg_all(event.participants.filter(~Q(id=requestor.id)), subject, body)            
            
            for profile in event.participants.all():
                event.participants.remove(profile)
                if profile in event.owners.all():
                    event.owners.remove(profile)
                event.save()
            
            event.delete() 
            
            data["success"] = "Successfully deleted event."            
    
    return HttpResponse(json.dumps(data), content_type="application/json")  

@login_required
def promote(request):
    ''' Promote one of the participants to an owner of the Event.
    Error if specified Event or UserProfile doesn't exist.
    Error if the requestor is not an owner.
    Error if the specified user is already an owner.
    Error if the specified user is not a participant.
    '''
   
    now = timezone.now() 
    data = {}
    
    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST['event_id']  
        user_id = request.POST['user_id']
    
        event = get_object_or_404(Event, id=event_id)
        profile = get_object_or_404(UserProfile, id=user_id) 
        requestor = UserProfile.objects.get(user_id=request.user.id)
    
        if requestor not in event.owners.all():
            data = errors("You do not have permission to perform this event.", data)           
        if event.end_time <= now:      
            data = errors("Cannot promote user. This event has ended.", data)
        if event.event_time <= now and now <= event.end_time:
            data = errors("Cannot promote user. This event is currently in progress.", data)            
        if profile in event.owners.all() and requestor == profile:
            data = errors("Cannot promote user. You are already an owner for this event.", data)
        if profile in event.owners.all() and requestor != profile:   
            data = errors("Cannot promote user. This user is already an owner for this event", data)
        if profile not in event.participants.all():
            data = errors("Cannot promote user. This user is not a participant.", data)
        
        if 'error' not in data:
            event.owners.add(profile)
            event.save()
            
            subject = "%s has made you an owner" % all_info_one_profile(requestor)['username']
            body = "%s has made you an owner" % all_info_one_profile(requestor)['username']
            auto_msg(profile, subject, body)  
            
            data["success"] = "Successfully promoted user."

    return HttpResponse(json.dumps(data), content_type="application/json") 

@login_required
def demote(request):
    ''' Demote one of the owners of the Event to a participant.
    Error if specified Event or UserProfile doesn't exist.
    Error if the requestor is not an owner.
    Error if the specified user is not an owner.
    '''
    
    now = timezone.now()
    data = {}

    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST['event_id']  
        user_id = request.POST['user_id']        
    
        event = get_object_or_404(Event, id=event_id)
        profile = get_object_or_404(UserProfile, id=user_id) 
        requestor = UserProfile.objects.get(user_id=request.user.id)
        event_over = event.end_time <= now
    
        if requestor not in event.owners.all():
            data = errors("You do not have permission to perform this event.", data)         
        if event_over:
            data = errors("Cannot demote user. This event has ended.", data)  
        if event.event_time <= now and now <= event.end_time:
            data = errors("Cannot demote user. This event is currently in progress.", data)  
        if profile in event.owners.all() and requestor == profile and not event_over:
            data = errors("Cannot demote user. You may not demote yourself. \
            If you no longer wish to be an owner please select leave and rejoin the event.", data)  
        if profile not in event.owners.all() and requestor == profile:
            data = errors("Cannot demote user. You are not an owner for this event.", data)           
        if profile not in event.owners.all() and requestor != profile:
            data = errors("Cannot demote user. This user is not an owner for this event.", data)   
        if profile not in event.participants.all():
            data = errors("Cannot demote user. This user is not a participant.", data)            
        
        if 'error' not in data:
            event.owners.remove(profile)
            event.save()
            
            subject = "%s has removed you as owner" % all_info_one_profile(requestor)['username']
            body = "%s has removed you as owner" % all_info_one_profile(requestor)['username']
            auto_msg(profile, subject, body)            
    
            data["success"] = "Successfully demoted user."
    
    return HttpResponse(json.dumps(data), content_type="application/json") 

def kick(request):
    ''' Kick a user from the Event.
    Error if specified Event or UserProfile doesn't exist.
    Error if the requestor is not an owner.
    Error if the specified user is not a participant.
    '''
    
    now = timezone.now()
    data = {}
    
    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST['event_id']  
        user_id = request.POST['user_id'] 
        
        event = get_object_or_404(Event, id=event_id)
        profile = get_object_or_404(UserProfile, id=user_id) 
        requestor = UserProfile.objects.get(user_id=request.user.id)
        event_over = event.end_time <= now
    
        if requestor not in event.owners.all():
            data = errors("You do not have permission to perform this event.", data)            
        if event_over:  
            data = errors("Cannot kick user. This event has ended.", data)  
        if requestor == profile and not event_over:       
            data = errors("Cannot kick user. You may not kick yourself. \
            If you no longer wish to participate please select leave instead.", data)
        if profile not in event.participants.all():
            data = errors("Cannot kick user. This user is not a participant.", data)                    
        
        if 'error' not in data:
            if profile in event.owners.all():
                event.owners.remove(profile)             
            event.participants.remove(profile)  
            event.save()
            
            subject = "You have been kicked from the event"
            body = "You have been kicked from the event"
            auto_msg(profile, subject, body)       
            
            data["success"] = "Successfully kicked user."
    
    return HttpResponse(json.dumps(data), content_type="application/json")

### Event Searching ###
  
@login_required
@csrf_exempt
def events_name_search(request, nameQuery):
    ''' Get and return a list of all Events in location locQuery, separating them into events that are in_progress,
    upcoming, or have already ended. If locQuery is the empty string, returns the result of events(request).
    '''

    return events_search(request, nameQuery, '')

@login_required
@csrf_exempt
def events_loc_search(request, locQuery):
    ''' Get and return a list of all Events in location locQuery, separating them into events that are in_progress,
    upcoming, or have already ended. If locQuery is the empty string, returns the result of events(request).
    '''

    return events_search(request, '', locQuery)    

@login_required
@csrf_exempt
def events_search(request, nameQuery, locQuery):
    ''' Get and return a list of all Events in location locQuery, separating them into events that are in_progress,
    upcoming, or have already ended. If locQuery is the empty string, returns the result of events(request).
    '''

    msg = None
    
    if request.method == 'POST':
        if request.POST.get('msg', '') == 'deleted':
            msg = ('deleted')       

    now = timezone.now()
    name = nameQuery
    loc = locQuery
    in_progress = Event.objects.filter(event_time__lte=now, end_time__gte=now, location__contains=loc, name__contains=name)
    upcoming = Event.objects.filter(event_time__gt=now, location__contains=loc, name__contains=name)
    past = Event.objects.filter(end_time__lte=now, location__contains=loc, name__contains=name)
        
    context = {'in_progress': in_progress, 'upcoming': upcoming, 'past': past, 'msg': msg, 'location': loc, 'name': name}
    return render(request, 'app/search_events.html', context)
    
### Feedback related views ###

@login_required
def feedback(request, event_id):
    ''' Create new Feedback or edit existing Feedback.
    '''
    
    now = timezone.now()
    
    event = get_object_or_404(Event, id=event_id)
    profile = UserProfile.objects.get(user_id=request.user.id)
    others = event.participants.filter(~Q(id=profile.id))
    count = others.count()
    cutoff = event.end_time + timedelta(days=14)
    
    errors = {}   
    if profile not in event.participants.all():
        errors['not_participating'] = "Cannot leave feedback: you are not a participant of this event."
    if event.end_time > now:
        errors['too_early'] = "Cannot leave feedback: this event has not yet ended."
    if cutoff < now:
        errors['too_late'] = "Cannot leave feedback: the cutoff date for leaving feedback has passed."
     
    others_with_fb = []
    existing_fb = Feedback.objects.filter(event=event).filter(feedback_by=profile)
    fb_exists = existing_fb.count() > 0
    for fb in existing_fb:
        others_with_fb.append(fb.feedback_for)
        others = others.filter(~Q(id=fb.feedback_for.id))
    
    # Convert others (QuerySet) to List so it can be concatenated with other_with_fb
    tmp = []   
    for participant in others:
        tmp.append(participant)
    others = others_with_fb + tmp
    
    if fb_exists:
        extra = count - existing_fb.count()
        fbformset = modelformset_factory(Feedback, form=FeedbackForm, extra=extra)     
    else:
        fbformset = modelformset_factory(Feedback, form=FeedbackForm, extra=count)
    
    if request.method == 'POST' and not errors:
        formset = fbformset(request.POST, request.FILES, queryset=existing_fb)
        
        if formset.is_valid():
            for form in formset:
                tmp = form.save(commit=False)
                tmp.event = event
                tmp.feedback_by = profile
                if tmp.feedback == 'd':
                    if tmp.id:
                        tmp.delete()
                else:
                    tmp.save()
            return HttpResponseRedirect('/event/%d' % event.id)
        else:
            print formset.errors       
    else:
	formset = fbformset(queryset=existing_fb)
    
    others = all_info_many_profiles(others)
    
    return render(request, 'app/feedback.html', 
                  {'event': event, 'participants': others, 'formset': formset, 'errors': errors,
                   'existing_feedback': existing_fb}
                  )

### Comment related views ###

@login_required
def comment(request, event_id):
    ''' Create new Comment.
    '''
    
    context = RequestContext(request)
    now = timezone.now()
    event = get_object_or_404(Event, id=event_id)
    profile = UserProfile.objects.get(user_id=request.user.id)
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            note = comment_form.save(commit=False)
            note.author = profile
            note.event = event
            note.created = now
            note.save()
            return HttpResponseRedirect('/event/%d' % event.id)
    else:
        comment_form = CommentForm()
        
    return render(request, 'app/comment.html', 
                  {'event': event, 'profile': profile, 'comment_form': comment_form}
                  )

@login_required
def edit_comment(request, comment_id):
    ''' Edit a comment.
    '''

    data = {}
    comment = get_object_or_404(Comment, id=comment_id)    
    event = Event.objects.get(id=comment.event.id)
    profile = UserProfile.objects.get(user_id=request.user.id)

    #this needs change
    if profile!=comment.author and profile not in event.owners.all():
        data = errors("You do not have permission to edit this comment", data)
        return HttpResponse(json.dumps(data), content_type="application/json")        
    else:
        if request.method == "POST":
            form = EditCommentForm(request.POST)
            if form.is_valid():
                changes = form.cleaned_data
                comment.subject = changes['subject']
                comment.message = changes['message']
                comment.save()
                
                return HttpResponseRedirect('/event/%d' % event.id)
        else:
            form = EditCommentForm(instance=comment)
            
        context = {'event': event, 'comment': comment,'profile': profile, 'form': form}

        return render(request, 'app/edit_comment.html', context)

@login_required
def delete_comment(request):
    ''' Delete a comment.
    '''
    if request.method == 'POST' and request.is_ajax():
        event_id = request.POST['event_id']
        comment_id = request.POST['comment_id']
        
    data = {}
    comment = get_object_or_404(Comment, id=comment_id)
    event = Event.objects.get(id=event_id)
    profile = UserProfile.objects.get(user_id=request.user.id)

    participants = all_info_many_profiles(event.participants.all())    
    owners = all_info_many_profiles(event.owners.all())
    comments = Comment.objects.filter(event=event_id)
    
    context = {'event': event, 'participants': participants,'profile': profile, 'owners': owners, 'comments': comments}


    if profile!=comment.author and profile not in event.owners.all():
        data = errors("You do not have permission to delete this comment", data)
        return HttpResponse(json.dumps(data), content_type="application/json")

    else:
	comment.delete()
	data["success"] = "Successfully deleted comment."
	return HttpResponse(json.dumps(data), content_type="application/json")