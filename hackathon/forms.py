from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from hackathon.models import *
from localflavor.us.us_states import STATE_CHOICES
from localflavor.us.forms import USStateField
from ckeditor.widgets import CKEditorWidget
import re
from django.core.validators import ValidationError
from django.core.validators import RegexValidator
from django.core.validators import validate_email
from django.contrib.auth import authenticate, get_user_model
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EMPTY_VALUES


class UserloginForm(forms.Form):

    email = forms.CharField(error_messages={'required': 'Please enter the email'}, widget=forms.TextInput(attrs={'class':' text login_input form-control', 'type': 'email', 'placeholder': 'Email'}))
    password = forms.CharField(error_messages={'required': 'Please enter the password'}, widget=forms.PasswordInput(attrs={'class':' text login_input form-control','placeholder': 'Password'}))


class UserAdminCreationForm(forms.Form):

    first_name = forms.CharField(error_messages={'required': 'Please enter the first name'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'First name'}))

    last_name = forms.CharField(error_messages={'required': 'Please enter the last name'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Last name'}))

    email = forms.CharField(error_messages={'required': 'Please enter the email'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'type': 'email', 'placeholder': 'Email'}))

    password = forms.CharField(error_messages={'required': 'Please enter the password'}, widget=forms.PasswordInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Password'}))

    organization = forms.CharField(error_messages={'required': 'Please enter the organization'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Organization'}))

    position = forms.CharField(error_messages={'required': 'Please enter the position'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Position'}))

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()

        if re.match(r"\w[\w\.-]*@\w[\w\.-]+\.\w+", email) == None:
            raise forms.ValidationError('Email is not valid')
        if not email:
            raise forms.ValidationError('Enter email address.')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address')
        if User.objects.filter(email__iexact=email).count() > 0 or User.objects.filter(username__iexact=email).count() > 0:
            raise forms.ValidationError('Email already exists.')
        return email


class EventForm(forms.ModelForm):
    event_name = forms.CharField(error_messages={'required': 'Please enter the name'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Last name'}))
    event_details = forms.CharField(widget=CKEditorWidget())
    optional_event_details = forms.CharField(widget=CKEditorWidget())
    event_FAQ = forms.CharField(widget=CKEditorWidget())
    event_date = forms.DateField(required=True, label='Event date',
                                error_messages={'required': 'Please enter your event date'},
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control', 'placeholder': 'MM-DD-YYYY', 'type': 'text'}))

    YOUR_STATE_CHOICES = list(STATE_CHOICES)
    YOUR_STATE_CHOICES.insert(0, ('', 'Select a state'))
    state = USStateField(required=True, initial="Select a state", error_messages={'required': 'State is required'},
                         widget=forms.Select(choices=YOUR_STATE_CHOICES,
                                             attrs={'class': 'form-control', 'placeholder': 'state'}))

    start_time = forms.CharField(required=True, label='Start Date',
                                 error_messages={'required': 'Please enter your start time'},
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'text'}))

    end_time = forms.CharField(required=True, label='End Date',
                                 error_messages={'required': 'Please enter your end time'},
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-control', 'placeholder': 'HH:MM', 'type': 'text'}))

    # start_time = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
    # end_time = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))

    class Meta:
        model = Event
        fields = ('event_name', 'event_date', 'event_theme', 'participant_grade_level', 'start_time', 'end_time',
                  'location_name', 'location_address_1', 'location_address_2', 'state', 'city', 'zip_code', 'country',
                  'event_details', 'optional_event_details', 'event_FAQ', 'event_contact_name', 'event_contact_phone',
                  'event_contact_email', 'event_banner', 'event_access_code', 'registration_code')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['event_name'].required = True
        self.fields['participant_grade_level'].required = True
        self.fields['start_time'].required = True
        self.fields['end_time'].required = True
        self.fields['location_name'].required = True
        self.fields['city'].required = True
        self.fields['zip_code'].required = True
        self.fields['event_details'].required = True
        self.fields['event_contact_name'].required = True
        self.fields['event_contact_phone'].required = True
        self.fields['event_contact_email'].required = True
        self.fields['registration_code'].required = True
        self.fields['event_access_code'].required = True
        # print self.fields['start_time'],self.fields['end_time'],self.fields['event_date']


class UserStudentRegisterForm(forms.Form):
    SCHOOL = (
        ('------', 'Select an option'),
        ('school1', 'school1'),
        ('school2', 'school2'),
        ('school3', 'school3'),
        ('school4', 'school4'),
        ('school4', 'school5'),
        ('not_listed', 'not in the list')
    )
    AGE = (
        ('----', 'Select an option'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20')
    )
    GRADE = (
        ('----', 'Select an option'),
        ('K', 'K'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12')
    )

    first_name = forms.CharField(error_messages={'required': 'Please enter the first name'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'First name'}))

    last_name = forms.CharField(error_messages={'required': 'Please enter the last name'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Last name'}))

    email = forms.CharField(error_messages={'required': 'Please enter the email'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'type': 'email', 'placeholder': 'Email'}))

    password = forms.CharField(error_messages={'required': 'Please enter the password'}, widget=forms.PasswordInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Password'}))

    confirm_password = forms.CharField(error_messages={'required': 'Please enter the Confirm password'}, widget=forms.PasswordInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Confirm Password'}))

    school = forms.ChoiceField(choices=SCHOOL, error_messages={'required': 'Please select the school'},required=True)

    age = forms.ChoiceField(choices=AGE,required=True, error_messages={'required': 'Please select the age'})

    grade = forms.ChoiceField(choices=GRADE,required=True, error_messages={'required': 'Please select the grade'})

    school_not_listed = forms.CharField(required=False,error_messages={'required': 'Please enter the School if not listed'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'School'}))

    address1 = forms.CharField(required=False, error_messages={'required': 'Please enter the address 1'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Address 1'}))

    address2 = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Address 2'}))

    city = forms.CharField(error_messages={'required': 'Please enter the city'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'City'}))

    zip = forms.CharField(error_messages={'required': 'Please enter the zip'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Zip'}))

    YOUR_STATE_CHOICES = list(STATE_CHOICES)
    YOUR_STATE_CHOICES.insert(0, ('', 'Select a state'))
    state = USStateField(required=True, initial="Select a state", error_messages={'required': 'State is required'},
                         widget=forms.Select(choices=YOUR_STATE_CHOICES,
                                             attrs={'class': 'form-control', 'placeholder': 'state'}))

    phone = forms.CharField(error_messages={'required': 'Please enter the phone'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'Phone'}))

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()

        if re.match(r"\w[\w\.-]*@\w[\w\.-]+\.\w+", email) == None:
            raise forms.ValidationError('Email is not valid')
        if not email:
            raise forms.ValidationError('Enter email address.')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address')
        if User.objects.filter(email__iexact=email).count() > 0 or User.objects.filter(username__iexact=email).count() > 0:
            raise forms.ValidationError('Email already exists.')
        return email


class EventAccessCode(forms.Form):

    event_name = forms.CharField(error_messages={'required': 'Please enter the event_name'}, widget=forms.TextInput(attrs={'class':' text login_input form-control', 'readonly': True,}))
    access_code = forms.CharField(required=True, error_messages={'required': 'Please enter the access code'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'access code'}))


class EventRegistrationCode(forms.Form):

    event_name = forms.CharField(error_messages={'required': 'Please enter the event_name'}, widget=forms.TextInput(attrs={'class':' text login_input form-control', 'readonly': True,}))
    registration_code = forms.CharField(required=True, error_messages={'required': 'Please enter the registration code'}, widget=forms.TextInput(
        attrs={'class': ' text login_input form-control', 'placeholder': 'registration code'}))


class CommaSeparatedEmailField(forms.Field):
    description = _('Email addresses')

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(CommaSeparatedEmailField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return []

        value = [item.strip() for item in value.split(self.token) if item.strip()]

        return list(set(value))

    def clean(self, value):
        """
        Check that the field contains one or more 'comma-separated' emails
        and normalizes the data to a list of the email strings.
        """
        value = self.to_python(value)

        if value in EMPTY_VALUES and self.required:
            raise forms.ValidationError(_('This field is required.'))

        for email in value:
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError(_("'%s' is not a valid email address.") % email)
        return value


class ShareFlyerForm(forms.Form):
    email = CommaSeparatedEmailField()


class PasswordResetForm_pleasure(forms.Form):
    email = forms.EmailField(max_length=254,required=True,error_messages={'required':'Please Enter Your Email'}, widget=forms.TextInput(attrs={'class':'text login_input form-control','type':'email','placeholder':'Enter your email address'}))
    # email = forms.EmailField(label=_("Email"), max_length=254,required=True,error_messages={'required':'Please Enter Your Email'}, max_length=300, widget=forms.TextInput(attrs={'class':'text login_input form-control','type':'email','placeholder':'Enter your email address'})

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.

        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='reset_password/password_reset_subject.txt',
             email_template_name='reset_password/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            print "contextcontext", context
            e = self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)
            print "eeeeeeeeee", e
