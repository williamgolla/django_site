from django.contrib.auth.models import User
from app.models import UserProfile, Event
from django_messages.models import Message

def all_info_one_profile(profile):
    ''' Given a UserProfile, grab the associated User object and return all fields from both models.
    '''
    
    user = User.objects.get(id=profile.user_id)
    return {'id': profile.id, 'location': profile.location, 'username': user.username,
            'email': user.email, 'date_joined': user.date_joined.date(), 'last_login': user.last_login}    

def all_info_many_profiles(profiles):
    ''' Given a list of UserProfiles, grab the associated User objects and return all fields 
    from both models for each profile.
    '''
    
    users = []
    
    for profile in profiles:
        users.append(all_info_one_profile(profile))
    
    return users  

def auto_msg(profile, subject, body):
    ''' Given a profile get the associated user and send them a message from user AutoMessage.
    '''
    
    sender = User.objects.get(username='AutoMessage')    
    recipient = User.objects.get(id=profile.user_id)
    
    msg = Message(
            sender = sender,
            recipient = recipient,
            subject = subject,
            body = body,
                )
    msg.save()    

def auto_msg_all(profiles, subject, body):
    ''' Given a list of profiles get the associated users and send them a message from user AutoMessage.
    '''
    
    sender = User.objects.get(username='AutoMessage')
    
    for profile in profiles:
        recipient = User.objects.get(id=profile.user_id)
        msg = Message(
                sender = sender,
                recipient = recipient,
                subject = subject,
                body = body,
                    )
        msg.save()

def get_rep(feedback_for):
    ''' Computes and returns reputation for user specified in profile
    '''

    feedback_lists = {}
    rep = 0.0

    for f in feedback_for:
        if f.event.id not in feedback_lists.keys():
            feedback_lists[f.event.id] = [_rep_helper(f)]
        else:
            feedback_lists[f.event.id].append(_rep_helper(f))
    for l in feedback_lists.values():
        rep += average(l)
    return rep

def average(l):
    ''' Returns the average of all items in the list '''

    return sum(l)/len(l)

def _rep_helper(feedback):
    ''' Helper function for get_rep. Returns a numeric representation of feedback:
        Returns 1.0 for good, 0.0 for bad, -1.0 for noshow.
    '''

    if feedback.feedback == 'g':
        return 1.0
    if feedback.feedback == 'b':
        return -1.0
    if feedback.feedback == 'n':
        return 0.0

def make_friends(feedback_by, feedback_for):
    ''' Returns a list of user ids that are friends with the user specified in profile
    '''

    feed_for_me = {}
    feed_for_them = {}
    friends = []

    for f in feedback_by:
        if f.feedback_for.id not in feed_for_them.keys():
            feed_for_them[f.feedback_for.id] = [_rep_helper(f)]
        else:
            feed_for_them[f.feedback_for.id].append(_rep_helper(f))

    for f in feedback_for:
        if f.feedback_by.id in feed_for_them.keys():
            if f.feedback_by.id not in feed_for_me.keys():
                feed_for_me[f.feedback_by.id] = [_rep_helper(f)]
            else:
                feed_for_me[f.feedback_by.id].append(_rep_helper(f))

    for user in feed_for_them.keys():
        if user in feed_for_me.keys():
            myrating = average(feed_for_them[user])
            theirrating = average(feed_for_me[user])
            if myrating > 0 and theirrating > 0:
                friends.append(user)
    return friends
        
def errors(error, errors):
    ''' Add error to errors and return errors.
    '''
    
    if 'error' in errors:
        errors['error'] += '<br />' + error
    else:
        errors = {'error': error}
    
    return errors
    
