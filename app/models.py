import datetime

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    location = models.CharField(max_length=200, blank=True)
    
    def __unicode__(self):
        return self.user.username
    

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    event_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(UserProfile, related_name='created_by')
    created = models.DateTimeField()
    modified = models.DateTimeField()
    participants = models.ManyToManyField(UserProfile, related_name='events')
    owners = models.ManyToManyField(UserProfile, related_name='events_owned')
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        ''' On save, update timestamps.
        '''
        
        if not self.id:
            self.created = datetime.datetime.today()
        self.modified = datetime.datetime.today()
        
        return super(Event, self).save(*args, **kwargs)   
    
class Feedback(models.Model):
    event = models.ForeignKey(Event)
    feedback = models.CharField(max_length=1)
    feedback_by = models.ForeignKey(UserProfile, related_name='feedback_by')
    feedback_for = models.ForeignKey(UserProfile, related_name='feedback_for')
    comment = models.CharField(max_length=200, null=True, blank=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    
    def __unicode__(self):
        by = User.objects.get(id=self.feedback_by.user_id).username
        ffor = User.objects.get(id=self.feedback_for.user_id).username
        if self.feedback == 'g':
            feed = "positive feedback"
        elif self.feedback == 'b':
            feed = "negative feedback"
        elif self.feedback == 'n':
            feed = "noshow feedback"
        else:
            feed = self.feedback
        return '(' + self.event.name + ') ' + by + ' gave ' + ffor + ' ' + feed + ". COMMENT: " + self.comment
    
    def save(self, *args, **kwargs):
        ''' On save, update timestamps.
        '''
        
        if not self.id:
            self.created = datetime.datetime.today()
        self.modified = datetime.datetime.today()
        
        return super(Feedback, self).save(*args, **kwargs)
    
    @property
    def nice_fb(self):
        ''' Return nicely formatted versions of the feedback.
        '''
        
        if self.feedback == 'g':
            return "positive feedback."
        elif self.feedback == 'b':
            return "negative feedback."
        
        return "did not show."

class Comment(models.Model):
    event = models.ForeignKey(Event)
    author = models.ForeignKey(UserProfile, related_name='author')
    subject = models.CharField(max_length=200)
    message = models.CharField(max_length=200, null=True, blank=True)
    created = models.DateTimeField()

    def __unicode__(self):
        return str(self.author) + " POSTED " + self.message + " ON " + str(self.event)
