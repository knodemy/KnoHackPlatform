from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save


class UserProfile(models.Model):

    user = models.OneToOneField(User)

    # admin user fields
    organization = models.CharField(_('organization name'), max_length=255, null=True, blank=True)
    position = models.CharField(_('position title'), max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(_('admin'), default=False,
                                   help_text=_('Designates whether this user should be treated as '
                                               'admin. Unselect this instead of deleting accounts.'))

    # student user fields
    SCHOOL = (
        ('school1', 'school1'),
        ('school2', 'school2'),
        ('school3', 'school3'),
        ('school4', 'school4'),
        ('school4', 'school5')
    )
    AGE = (
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

    school = models.CharField(max_length=100, choices=SCHOOL, null=True, blank=True)
    age = models.CharField(_('age'), max_length=255, choices=AGE, null=True, blank=True)
    grade = models.CharField(_('grade'), max_length=255, choices=GRADE, null=True, blank=True)
    school_not_listed = models.CharField(_('school_not_listed'), max_length=255, null=True, blank=True)
    address_1 = models.CharField(_('address_1'), max_length=255, null=True, blank=True)
    address_2 = models.CharField(_('address_2'), max_length=255, null=True, blank=True)
    city = models.CharField(_('city'), max_length=255, null=True, blank=True)
    state = models.CharField(_('state'), max_length=2, null=True, blank=True)
    zip = models.CharField(_('zip'), max_length=255, null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=255, null=True, blank=True)
    passwor_reset_token = models.CharField(_('password_reset_token'), max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username


class Event(models.Model):

    event_name = models.CharField(max_length=75, blank=True)
    event_theme = models.CharField(max_length=75, blank=True)
    event_date = models.DateField()
    GRADE_CHOICE = (
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
        ('12', '12'),
    )

    participant_grade_level = models.CharField(choices=GRADE_CHOICE, max_length=30, blank=True)

    min_grade = models.IntegerField(choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6),
                                                    (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)),
                                                    null=True, blank=True)
    max_grade = models.IntegerField(choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6),
                                                    (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)),
                                                    null=True, blank=True)
    time_zone = models.CharField(max_length=15, help_text="ex: PST", blank=True)
    start_time = models.TimeField(help_text="Please use 24 hour time.", null=True, blank=True)
    end_time = models.TimeField(help_text="Please use 24 hour time.", null=True, blank=True)
    location_name = models.CharField(max_length=75, help_text="ex: Pleasanton Library", blank=True)
    location_address_1 = models.CharField(max_length=75, help_text="ex: 400 Old Bernal Ave", blank=True)
    location_address_2 = models.CharField(max_length=75, help_text="ex: Building 2, Lobby, etc.", blank=True)
    city = models.CharField(max_length=75, help_text="ex: Pleasanton", blank=True)
    state = models.CharField(max_length=2, help_text="ex: CA", blank=True)
    zip_code = models.CharField(max_length=5, help_text="ex: 94566", blank=True)
    country = models.CharField(max_length=75, help_text="ex: United States", blank=True)
    event_details = RichTextField(help_text="Detailed description of your event goes here.")
    optional_event_details = RichTextField(help_text="Additional detailed description of your event goes here.", blank=True, null=True)
    event_FAQ = RichTextField(help_text="FAQs go here.", blank=True, null=True)
    event_contact_name = models.CharField(max_length=30, help_text="Name of the contact for your event.", blank=True)
    event_contact_phone = models.CharField(max_length=30, help_text="Phone number of the contact for your event.", blank=True)
    event_contact_email = models.CharField(max_length=255, help_text="Email of the contact for your event.", blank=True)
    event_banner = models.FileField(upload_to='images/',
                    help_text="Dimensions: minimum 2160 x 1080px. File Type: JPEG, PNG, BMP, or GIF. File Size: no larger than 10 MB.",
                    null=True, blank=True)
    event_access_code = models.CharField(max_length=10, help_text="clarify: 10 or fewer character access code for your event.", blank=True)
    registration_code = models.CharField(max_length=10,
                                         help_text="clarify: 10 or fewer character registration code for your event.",
                                         blank=True)

    creator = models.ForeignKey(User, null=True, blank=True)
    event_register = models.ManyToManyField(User, through='EventRegister', related_name='event_register', blank=True)
    # event_team = models.ManyToManyField('Teams', related_name='event_team', blank=True)

    def __unicode__(self):
        return self.event_name

    def __str__(self):
        return self.event_name


class EventRegister(models.Model):
    TYPE_CHOICE = (
        ('-----', '-----'),
        ('ACCESS_CODE', 'ACCESS_CODE'),
        ('REGISTRATION_CODE', 'REGISTRATION_CODE'),
        ('BOTH', 'BOTH'),
    )

    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    type = models.CharField(choices=TYPE_CHOICE, null=True, blank=True, max_length=25)
    registration_code = models.CharField(max_length=255, null=True, blank=True)
    access_code = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event.event_name


class ProgramFlow(models.Model):

    event = models.OneToOneField(Event)

    welcome_slide_title = models.CharField(max_length=255, null=True, blank=True)
    welcome_slide_file = models.CharField(max_length=255, null=True, blank=True)
    welcome_talking_points = RichTextField(max_length=1000, default=None, null=True, blank=True)
    welcome_boolean = models.BooleanField(default=False)
    welcome_slide_file_id = models.CharField(max_length=255, null=True, blank=True)

    guest_speaker_slide_title = models.CharField(max_length=255, null=True, blank=True)
    guest_speaker_slide_file = models.CharField(max_length=255, null=True, blank=True)
    guest_speaker_talking_points = RichTextField(max_length=1000, default=None, null=True, blank=True)
    guest_speaker_boolean = models.BooleanField(default=False)
    guest_speaker_slide_id = models.CharField(max_length=255, null=True, blank=True)

    workshop_slide_title = models.CharField(max_length=255, null=True, blank=True)
    workshop_slide_file = models.CharField(max_length=255, null=True, blank=True)
    workshop_talking_points = RichTextField(max_length=1000, default=None, null=True, blank=True)
    workshop_boolean = models.BooleanField(default=False)
    workshop_slide_file_id = models.CharField(max_length=255, null=True, blank=True)

    number_of_teams = models.IntegerField(null=True, blank=False)
    team_project_slide_title = models.CharField(max_length=255, null=True, blank=True)
    team_project_slide_file = models.CharField(max_length=255, null=True, blank=True)
    team_project_talking_points = RichTextField(max_length=1000, default=None, null=True, blank=True)
    team_project_boolean = models.BooleanField(default=False)
    team_project_slide_file_id = models.CharField(max_length=255, null=True, blank=True)

    team_slideshow_slide_title = models.CharField(max_length=255, null=True, blank=True)
    team_slideshow_slide_file = models.CharField(max_length=255, null=True, blank=True)
    team_slideshow_talking_points = RichTextField(max_length=1000, default=None, null=True, blank=True)
    team_slideshow_boolean = models.BooleanField(default=False)
    team_slideshow_slide_file_id = models.CharField(max_length=255, null=True, blank=True)

    judges_slide_title = models.CharField(max_length=255, null=True, blank=True)
    judges_slide_file = models.CharField(max_length=255, null=True, blank=True)
    judges_talking_points = RichTextField(max_length=1000, default=None, null=True, blank=True)
    judges_boolean = models.BooleanField(default=False)
    judges_slide_file_id = models.CharField(max_length=255, null=True, blank=True)

    creator = models.ForeignKey(User, null=True, blank=True, editable=False)

    def __str__(self):
        return self.event.event_name


class Teams(models.Model):
    creator = models.ForeignKey(User, null=True, blank=True)
    team_name = models.CharField(max_length=255)
    user_team = models.ManyToManyField(User, related_name='user_team', blank=True)


# signal to create profile when user get registered
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)