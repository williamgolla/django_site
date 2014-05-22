# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.contrib.auth.models import User

from app.models import UserProfile, Event, Feedback, Comment
from app.fields import JqSplitDateTimeField
from app.widgets import JqSplitDateTimeWidget

class UserForm(forms.ModelForm):
    
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserProfileForm(forms.ModelForm):
    ''' This form is used with the UserForm above when creating a new User/UserProfile.
    '''
    
    class Meta:
        model = UserProfile
        fields = ['location']

class EditUserForm(forms.Form):
    ''' This form is used to edit a User/UserProfile object.
    '''

    current_password = forms.CharField(widget=forms.PasswordInput(), label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput(), label="New Password", required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password", required=False)
    email = forms.EmailField(required=False)
    location = forms.CharField(max_length=200, required=False)

    def clean(self):
        data = super(EditUserForm, self).clean()
        new_pass = data.get("new_password")
        conf_pass = data.get("confirm_password")
        if new_pass != conf_pass:
            raise forms.ValidationError("New password must match Confirm Password")
        return data

class EventForm(forms.ModelForm):
    ''' This form is used when creating a new Event.
    '''
    
    ## This should work...
    #event_time = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class':'datepicker','time_class':'timepicker'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': '6', 'cols':'35'}))
    event_time = forms.DateTimeField(input_formats=['%m/%d/%Y %H:%M'])
    end_time = forms.DateTimeField(input_formats=['%m/%d/%Y %H:%M'])
    
    def clean_event_time(self):
        data = self.cleaned_data['event_time']
        
        if not data:
            raise forms.ValidationError("You must specify an event time.")  
        
        return data
    
    def clean_end_time(self):
        data = self.cleaned_data['end_time']
        
        if not data:
            raise forms.ValidationError("You must specify an end time.")  
        
        return data    
    
    def clean(self):
        data = super(EventForm, self).clean()               
        event_time = data.get("event_time")
        end_time = data.get("end_time")
        
        if not event_time:
            raise forms.ValidationError("You must specify an event time.")  
        
        if not end_time:
            raise forms.ValidationError("You must specify an end time.") 
        
        if end_time <= event_time:
            raise forms.ValidationError("Action end time must be later than the start time")            
        
        return data
        
    class Meta:
        model = Event
        fields = ['name','description','location','event_time', 'end_time']

class EditEventForm(forms.ModelForm):
    ''' This form is used to edit an existing Event
    '''

    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': '6', 'cols':'35'}), required=False)
    location = forms.CharField(required=False)
    event_time = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'], required=False)
    end_time = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'], required=False)

    def clean(self):
        data = super(EditActionForm, self).clean()
        event_time = data.get("event_time")
        end_time = data.get("end_time")

        if event_time and end_time:
            if end_time <= event_time:
                raise forms.ValidationError("Event end time must be later than the start time")
        return data
    
    class Meta:
        model = Event
        fields = ['name','description','location','event_time', 'end_time']

class FeedbackForm(forms.ModelForm):
    ''' This form is used when creating new feedback.
    '''
    
    choices = (('g', '(+1) Positive'),
               ('n', '(±0) Neutral'),
               ('b', '(-1) Negative'),
               ('d', 'No Feedback'))
    feedback = forms.ChoiceField(widget=forms.RadioSelect(), choices=choices, initial='d')
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': '6', 'cols':'35'}), required=False)
        
    class Meta:
        model = Feedback
        fields = ['feedback_for','feedback','comment']

class CommentForm(forms.ModelForm):
    ''' This form is used when creating a new comment
    '''

    subject =  forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ['subject','message']

class EditCommentForm(forms.ModelForm):
    ''' This form is used to edit a Comment object.
    '''

    message = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = Comment
        fields = ['subject','message']
