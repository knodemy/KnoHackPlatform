from django.shortcuts import render, HttpResponseRedirect, redirect, HttpResponse
from hackathon.models import *
from hackathon.forms import *
from django.contrib.auth import authenticate, logout, login as LoginUser
from django.contrib.auth.models import User
from hackathon.models import UserProfile
import boto
import os
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import datetime
from googleapiclient.discovery import build
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
gauth = GoogleAuth()

# Email of the Service Account
SERVICE_ACCOUNT_EMAIL = 'service account email'
# Path to the Service Account's Private Key file
SERVICE_ACCOUNT_PKCS12_FILE_PATH = 'service account key path'


def index(request):
    return render(request, 'welcome.html')


def admin_index(request):
    return render(request, 'welcome.html')


def create_drive_service(user_email):
    """Build and returns a Drive service object authorized with the service accounts
    that act on behalf of the given user.

    Args:
      user_email: The email of the user.
    Returns:
      Drive service object.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_EMAIL,
        SERVICE_ACCOUNT_PKCS12_FILE_PATH,
        'notasecret',
        scopes=['https://www.googleapis.com/auth/drive'])

    credentials = credentials.create_delegated(user_email)

    return build('drive', 'v2', credentials=credentials)


def custom_user_login(request):

    """ Users login form. Authenticate the user

    Form Fields:
        email: email of the user
        password: password of the user

    Returns:
        user authenticated object
        redirect to admin or event list base on user status ( admin or normal user )
    """

    form = None
    error = None
    form = UserloginForm()
    if request.method == 'POST':
        form = UserloginForm(request.POST, None)
        if form.is_valid():
            data = form.cleaned_data
            password = data['password']
            email = data['email']

            print "password: ", password
            print "email: ", email

            user_auth = authenticate(username=email, password=password)
            print "user_auth: ", user_auth
            if user_auth is not None:
                LoginUser(request, user_auth)
                user_profile = UserProfile.objects.get(user__email=email)
                # if user_profile.passwor_reset_token:
                #     user_profile.passwor_reset_token = None
                #     user_profile.save()

                # if user admin redirect to admin dashboard else redirect to event list
                if user_profile.is_admin:

                    return redirect('admin_dashboard')
                else:
                    return redirect('/eventlist/')

            else:
                error = "Please enter correct email/password"
                return render(request, 'login.html', {
                    'form': form,
                    'error': error,
                })

        else:
            errors_dict = {}
            if form.errors:
                for error in form.errors:
                    error = form.errors[error]
                    print 'e', error

    return render(request, 'login.html' ,{
        'form': form,
        'error': error,
    })


def logout_user(request):

    """ Logout out the user

    Args:
        request objects
    Returns:
        return to login page
    """

    logout(request)
    return redirect('login')


def login_default(request):

    return render(request,'knodemy/default_pages/login_view_default.html')


def admin_default_page(request):

    return render(request,'knodemy/default_pages/admin_default_page.html')


# admin registration view
def register_user_admin(request):

    """ Registration form of admin

    Form Fields:
        email: email of the user
        password: password of the user
        first name: first name of the user
        last name: last name of the user
        organization: organization of the user
        position: position of the user

    Returns:
        user authenticated object
        redirect to admin dashboard
    """


    form = None
    error = None
    form = UserAdminCreationForm()
    if request.method == 'POST':
        form = UserAdminCreationForm(request.POST, None)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            password = data['password']
            first_name = data['first_name']
            last_name = data['last_name']
            organization = data['organization']
            position = data['position']

            user = User.objects.create(username=email, email=email)
            user.set_password(password)
            user.save()

            user_profile = user.userprofile
            try:
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                user_profile.organization = organization
                user_profile.position = position

                # make is_admin true to create user as a admin
                user_profile.is_admin = True
                user_profile.save()

                # authenticating user
                user_auth = authenticate(username=email, password=password)
                if user_auth is not None:
                    LoginUser(request, user_auth)
                    print "user_auth: ", user_auth
                    return redirect('admin_dashboard')
                else:
                    print "user_auth: ", user_auth
                    return redirect('login')

            except Exception as e:
                error = e

        else:
            errors_dict = {}
            if form.errors:
                for error in form.errors:
                    error = form.errors[error]
                    print 'e', error

    return render(request, 'signup.html', {
        'form': form,
        'error': error,
    })


# student registration view
def register_user_student(request):

    """ Registration form of student

    Form Fields:
        email: email of the user
        password: password of the user
        first name: first name of the user
        last name: last name of the user
        school: school of the user
        age: age of the user
        grade: grade of the user
        address1: address1 of the user
        address2: address2 of the user
        city: city of the user
        zip: zip of the user
        state: state of the user
        phone: phone of the user

    Returns:
        user authenticated object
        redirect to student dashboard
    """


    form = None
    error = None
    form = UserStudentRegisterForm()
    if request.method == 'POST':
        form = UserStudentRegisterForm(request.POST, None)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            password = data['password']
            first_name = data['first_name']
            last_name = data['last_name']
            school = data['school']
            school_not_listed = data['school_not_listed']
            age = data['age']
            grade = data['grade']
            address1 = data['address1']
            address2 = data['address2']
            city = data['city']
            zip = data['zip']
            state = data['state']
            phone = data['phone']

            user = User.objects.create(username=email, email=email)
            user.set_password(password)
            user.save()

            user_profile = user.userprofile
            try:

                user.first_name = first_name
                user.last_name = last_name
                user.save()

                # make is_admin false to register user as a normal user
                user_profile.is_admin = False

                user_profile.school = school
                user_profile.school_not_listed = school_not_listed
                user_profile.age = age
                user_profile.grade = grade
                user_profile.address_1 = address1
                user_profile.address_2 = address2
                user_profile.city = city
                user_profile.zip = zip
                user_profile.state = state
                user_profile.phone = phone

                print "info saved", email, address1,address1,school,school_not_listed

                user_profile.save()

                user_auth = authenticate(username=email, password=password)
                if user_auth is not None:
                    LoginUser(request, user_auth)
                    print "user_auth: ", user_auth
                    return redirect('/studentdashboard/')
                else:
                    return redirect('/login/')

            except Exception as e:
                error = e
                print "error: ", e

        else:
            errors_dict = {}
            if form.errors:
                for error in form.errors:
                    error = form.errors[error]
                    print 'e', error

    return render(request, 'student_signup.html', {
        'form': form,
        'error': error,
    })


def admin_dashboard(request):

    return render(request, 'admin_dashboard.html',)


def student_dashboard(request):

    return render(request, 'event_search.html')


def share_flyer(request):

    form = ShareFlyerForm()
    if request.POST:
        form = ShareFlyerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            for e in email:
                print "E", e

    return render(request, 'share_flyer.html', {
        'form': form
    })


# student profile view
@login_required(login_url='/login/')
def student_profile(request):

    """ Student profile form

    Form Fields:
        confirm: confirm of the user
        first_name: first_name of the user
        last_name: last_name of the user
        last name: last name of the user
        school: school of the user
        age: age of the user
        grade: grade of the user
        address1: address1 of the user
        address2: address2 of the user
        city: city of the user
        zip: zip of the user
        state: state of the user
        phone: phone of the user

    Returns:
        update the student profile information
        redirect to student profile
    """

    error = None
    email = request.user.email

    user = User.objects.get(username=email)
    if request.method == 'POST':
        req = request.POST
        password = req['confirm']
        first_name = req['first_name']
        last_name = req['last_name']
        school = req['school']

        age = req['age']
        grade = req['grade']
        address1 = req['address1']
        address2 = req['address2']
        city = req['city']
        zip = req['zip']
        state = req['state']
        phone = req['phone']

        try:
            custom_user = user
            if password:

                # setting the user password
                custom_user.set_password(password)

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            user_profile = user.userprofile
            user_profile.is_admin = False
            user_profile.school = school
            user_profile.age = age
            user_profile.grade = grade
            user_profile.address_1 = address1
            user_profile.address_2 = address2
            user_profile.city = city
            user_profile.zip = zip
            user_profile.state = state
            user_profile.phone = phone

            print "info saved", email, address1, address1, school

            user_profile.save()

            return redirect('/studentprofile/')

        except Exception as e:
            error = e
            print "error: ", e

    return render(request, 'student_profile.html', {
        'error': error,
        'user':user

    })


# student detail view
def student_detail(request, id):

    student = None
    try:
        student = User.objects.get(id=int(id))
    except:
        pass

    return render(request, 'student_detail.html', {
        'student': student,
    })


def event_profile(request, id):

    event = None
    try:
        event = Event.objects.get(id=int(id))
    except:
        pass
    return render(request, 'event_profile.html', {
        'event': event
    })


# admin profile view
@login_required(login_url='/login/')
def admin_profile(request):

    """ Admin profile form

    Form Fields:
        confirm: confirm of the user
        first_name: first_name of the user
        last_name: last_name of the user
        last name: last name of the user
        organization: organization of the user
        position: position of the user


    Returns:
        update the admin profile information
        redirect to admin profile
    """

    error = None
    email = request.user.email
    print "request: ", request
    print "email: ", email
    user = User.objects.get(username=email)
    if request.method == 'POST':
        req = request.POST
        password = req['confirm']
        first_name = req['first_name']
        last_name = req['last_name']
        organization = req['organization']
        position = req['position']

        try:
            custom_user = user
            if password:
                custom_user.set_password(password)

            custom_user.first_name = first_name
            custom_user.last_name = last_name
            custom_user.save()

            user_profile = custom_user.userprofile
            user_profile.organization = organization
            user_profile.position = position
            user_profile.save()
            print "info saved", position, organization

            custom_user.save()

            return redirect('/adminprofile/')

        except Exception as e:
            error = e
            print "error: ", e

    return render(request, 'admin_profile.html', {
        'error': error,
        'user': user

    })


# create event view
@login_required(login_url='/login/')
def create_event(request):
    form = None
    error = None
    form = EventForm()
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            return HttpResponseRedirect('/programflow/'+str(event.id)+'')
        else:
            errors_dict = {}
            if form.errors:
                for error in form.errors:
                    error = form.errors[error]
                    print 'e', error

    return render(request, 'create_event.html', {
        'form': form,
        'error': error
    })


# create team view
@login_required(login_url='/login/')
def create_team(request):

    """ Create team form

    Form Fields:
        team_name: team_name of the team
        event: event of the team
        students: student of the team


    Returns:
        create the new team object
    """

    form = None
    error = None
    event_obj = None
    student = User.objects.filter(userprofile__is_admin=False)
    print "students ", student
    event = Event.objects.all()
    if request.method == 'POST':

        team_name = request.POST.get('team_name', None)
        event = request.POST.get('event', None)
        student = request.POST.getlist('student', None)

        team = Teams.objects.create(creator=request.user, team_name=team_name)
        # attaching student with team
        for s in student:
            team.user_team.add(s)

        team.save()

        # event_obj = Event.objects.get(id=int(event))
        # event_obj.event_team.add(team)

        print "team_name", team_name
        # print "event", event
        print "student", student

    return render(request, 'create_team.html', {
        'form': form,
        'error': error,
        'student': student,
        'event': event
    })


# edit event view
@login_required(login_url='/login/')
def edit_event(request, id):

    event = Event.objects.get(id=int(id))
    form_initial = {
        'event_name': event.event_name,
        'event_date': event.event_date,
        'event_theme': event.event_theme,
        'participant_grade_level': event.participant_grade_level,
        'start_time': event.start_time,
        'end_time': event.end_time,
        'location_name': event.location_name,
        'location_address_1': event.location_address_1,
        'location_address_2': event.location_address_2,
        'state': event.state,
        'city': event.city,
        'zip_code': event.zip_code,
        'country': event.country,
        'event_details': event.event_details,
        'optional_event_details': event.optional_event_details,
        'event_FAQ': event.event_FAQ,
        'event_contact_name': event.event_contact_name,
        'event_contact_phone': event.event_contact_phone,
        'event_contact_email': event.event_contact_email,
        'event_banner': event.event_banner,
        'event_access_code': event.event_access_code,
        'registration_code': event.registration_code,
    }
    print "edit: ", form_initial['event_name']
    form = None
    error = None
    form = EventForm(initial=form_initial)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            data = form.cleaned_data

            event.event_name = data['event_name']
            event.event_date = data['event_date']
            event.creator = request.user
            event.event_theme = data['event_theme']
            event.participant_grade_level = data['participant_grade_level']
            event.start_time = data['start_time']
            event.end_time = data['end_time']
            event.location_name = data['location_name']
            event.location_address_1 = data['location_address_1']
            event.location_address_2 = data['location_address_2']
            event.state = data['state']
            event.city = data['city']
            event.zip_code = data['zip_code']
            event.country = data['country']
            event.event_details = data['event_details']
            event.optional_event_details = data['optional_event_details']
            event.event_FAQ = data['event_FAQ']
            event.event_contact_name = data['event_contact_name']
            event.event_contact_phone = data['event_contact_phone']
            event.event_contact_email = data['event_contact_email']
            event.event_banner = data['event_banner']
            event.event_access_code = data['event_access_code']
            event.event_access_code = data['event_access_code']
            event.registration_code = data['registration_code']
            event.save()

            print "eventname: ",event.event_name
            event.save()
            return redirect('admin_dashboard')
        else:
            print "form not valid"
            errors_dict = {}
            if form.errors:
                for error in form.errors:
                    error = form.errors[error]
                    print 'e: ', error
    else:
        print "method not posted"
    return render(request, 'edit_event.html', {
        'form': form,
        'error': error
    })


# event list view
from django.db.models import Q
@login_required(login_url='/login/')
def event_list(request):

    today = datetime.datetime.today().date()
    print "today: ", today
    event = Event.objects.all()

    # event = Event.objects.filter(start_time__gte=today,
    #                              end_time__lte=today)
    if request.POST:
        if 'event-btn' in request.POST:
            event_name = request.POST.get('q', None)

            # Event.objects.filter(start__gte=datetime.datetime.combine(today, datetime.time.min),
            #                      end__lte=datetime.datetime.combine(today, datetime.time.max))
            if event:
                event = event.filter(event_name__icontains=event_name)

    return render(request, 'event_search.html', {
        'event': event
    })


@login_required(login_url='/login/')
def manage_events(request):
    today = datetime.datetime.today().date()
    print "today: ", today

    event = None
    userprofile = request.user.userprofile

    # if user is_staff then show all events
    if request.user.is_staff:
        event = Event.objects.all()

    # if user is_admin then show only filter event
    elif userprofile.is_admin:
        event = Event.objects.filter(creator=request.user)

    # event = Event.objects.filter(start_time__gte=today,
    #                              end_time__lte=today)

    if request.POST:
        if 'event-btn' in request.POST:
            event_name = request.POST.get('q', None)

            # Event.objects.filter(start__gte=datetime.datetime.combine(today, datetime.time.min),
            #                      end__lte=datetime.datetime.combine(today, datetime.time.max))

            # searching the event against q
            if event:
                event = event.filter(event_name__icontains=event_name)

    return render(request, 'manage_event.html', {
        'event': event
    })


@login_required(login_url='/login/')
def knohack_event_login(request, id):

    event = Event.objects.get(id=int(id))
    form_initial = {
        'event_name': event.event_name
    }
    form = EventAccessCode(initial=form_initial)

    if request.POST:
        if request.method == 'POST':
            form = EventAccessCode(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                event_name = data['event_name']
                access_code = data['access_code']

                if event.event_access_code == access_code:
                    event_register = EventRegister.objects.get_or_create(user=request.user, event=event)[0]
                    event_register.type = 'ACCESS_CODE'
                    event_register.access_code = access_code
                    event_register.save()

                    print "access code register: ", event_register
                    return HttpResponseRedirect('/studentflow/'+str(id)+'')

                else:
                    return redirect('event_list')

    return render(request, 'event_access_code.html', {
        'event': event,
        'form': form
    })


@login_required(login_url='/login/')
def registration_for_event(request, id):

    event = Event.objects.get(id=int(id))
    form_initial = {
        'event_name': event.event_name
    }
    form = EventRegistrationCode(initial=form_initial)

    if request.POST:
        if request.method == 'POST':
            form = EventRegistrationCode(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                event_name = data['event_name']
                registration_code = data['registration_code']

                if event.registration_code == registration_code:
                    event_register = EventRegister.objects.get_or_create(user=request.user, event=event)[0]
                    event_register.type = 'REGISTRATION_CODE'
                    event_register.registration_code = registration_code
                    event_register.save()

                    print "registration code: ", event_register

                return HttpResponseRedirect('/studentflow/' + str(id) + '')

    return render(request, 'event_registration_code.html', {
        'event': event,
        'form': form
    })


def how_it_work(request):
    user = request.user

    return render(request, 'how_it_works.html',{'user':user})


def student_team_list(request):

    return render(request, 'knodemy/student_team/student_team_list.html')


def student_attendees_list(request, id):

    attendees = Event.objects.prefetch_related('event_register').get(id=int(id))
    return render(request, 'student_attendees_list.html', {
        'attendees': attendees
    })

@login_required(login_url='/login/')
def event_delete(request, id):

    Event.objects.get(id=int(id)).delete()
    next_url = request.GET.get('next', None)
    print "next_url: ", next_url
    if next_url:
        return HttpResponseRedirect(next_url)

    return redirect('manage_events')

@login_required(login_url='/login/')
def event_detail(request, id):
    event = Event.objects.get(id=int(id))

    return render(request, 'event_detail.html', {
        'event': event
    })


@login_required(login_url='/login/')
def student_flow(request, id):
    event = Event.objects.get(id=int(id))
    program = ProgramFlow.objects.get(event=event)
    return render(request, 'student_side_program_flow.html', {
        'program': program
    })

@login_required(login_url='/login/')
def student_events(request):
    user = request.user
    # event = EventRegister.objects.filter(user=user).select_related('user')
    event = Event.objects.filter(event_register=user)
    print "query: ",event.query
    print "myevents: ", event


    context = {
        'event':event,
    }
    return render(request, 'student_event_list.html', context)



from knohack import settings
# this method is used to store the file
def save_file(f):
    original_name, file_extension = os.path.splitext(f.name)
    filename = original_name.replace(' ', '').replace('(', '-').replace(')', '-') + '-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + file_extension
    url = filename
    path = url
    destination = open(path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return path


# this method is used to upload the file on google drive using the google service account
def google_drive_upload(file):
    original_name, file_extension = os.path.splitext(file.name)

    scopes = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'google service account json file', scopes=scopes)

    # authenticating the google service account
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)
    print "drive: ", drive

    f = save_file(file)

    file_name_upload = '{}{}'.format(original_name, file_extension)

    file1 = drive.CreateFile({'title': file_name_upload})
    file1.SetContentFile(f)

    file1.Upload()
    permission = file1.InsertPermission({
        'type': 'anyone',
        'reader': 'anyone',
        'role': 'writer',
        'withLink': True})

    print("permission: ", permission)
    print "file: ", file1
    print(file1['alternateLink'])

    print file1.uploaded
    print('title: %s, id: %s' % (file1['title'], file1['id'] ))

    response = {'title': file1['title'], 'link': file1['alternateLink'], 'remove': f, 'id': file1['id']}

    return response


@login_required(login_url='/login/')
def program_flow(request, id):
    event = Event.objects.get(id=id)
    program_flow = ProgramFlow.objects.get_or_create(event=event)[0]
    print "event: ", event
    if request.POST:

        if 'welcomesubmit' in request.POST and request.FILES:
            print "welcomesubmit: "
            welcomefile = request.FILES.get('welcomefile')
            welcompublic = request.POST.get('welcompublic')
            welcome_text = request.POST.get('welcome_text')

            path = save_file(welcomefile)

            original_name, file_extension = os.path.splitext(welcomefile.name)
            file_name_upload = '{}{}'.format(original_name, file_extension)

            link = google_drive_upload(welcomefile)

            print "path: ", path
            print "link: ", link
            print "link: ", link['link']

            program_flow.welcome_slide_file = link['link']
            program_flow.welcome_slide_title = file_name_upload
            program_flow.welcome_slide_file_id = link['id']
            program_flow.welcome_talking_points = welcome_text
            program_flow.welcome_boolean = welcompublic
            # program_flow.welcome_slide_type = link['type']
            program_flow.save()

            os.remove(link['remove'])

        elif 'guestspeakersubmit' in request.POST and request.FILES:
            print "guestspeakersubmit: "
            guestspeaker_file = request.FILES.get('guestspeaker_file')
            guestspeakerpublic = request.POST.get('guestspeakerpublic')
            guestspeaker_text = request.POST.get('guestspeaker_text')

            path = save_file(guestspeaker_file)

            original_name, file_extension = os.path.splitext(guestspeaker_file.name)
            file_name_upload = '{}{}'.format(original_name, file_extension)

            link = google_drive_upload(guestspeaker_file)

            print "path: ", path
            print "link: ", link
            print "link: ", link['link']

            program_flow.guest_speaker_slide_file = link['link']
            program_flow.guest_speaker_slide_title = file_name_upload
            program_flow.guest_speaker_slide_id = link['id']
            program_flow.guest_speaker_talking_points = guestspeaker_text
            program_flow.guest_speaker_boolean = guestspeakerpublic
            # program_flow.guest_speaker_type = link['type']
            program_flow.save()

            os.remove(link['remove'])

        elif 'workshopsubmit' in request.POST and request.FILES:
            print "workshopsubmit: "
            workshopfile = request.FILES.get('workshopfile')
            workshoppublic = request.POST.get('workshoppublic')
            workshop_text = request.POST.get('workshop_text')

            path = save_file(workshopfile)

            original_name, file_extension = os.path.splitext(workshopfile.name)
            file_name_upload = '{}{}'.format(original_name, file_extension)

            link = google_drive_upload(workshopfile)

            print "path: ", path
            print "link: ", link
            print "link: ", link['link']

            program_flow.workshop_slide_file = link['link']
            program_flow.workshop_slide_title = file_name_upload
            program_flow.workshop_slide_file_id = link['id']
            program_flow.workshop_talking_points = workshop_text
            program_flow.workshop_boolean = workshoppublic
            # program_flow.workshop_slide_type = link['type']
            program_flow.save()

            os.remove(link['remove'])
            print "preview: ",  link

        elif 'teamprojectsubmit' in request.POST and request.FILES:
            print "teamprojectfile: "
            teamprojectfile = request.FILES.get('teamprojectfile')
            teamprojectpublic = request.POST.get('teamprojectpublic')
            teamproject_text = request.POST.get('teamproject_text')
            team_number = request.POST.get('team_number')
            print "file", teamprojectfile

            path = save_file(teamprojectfile)

            original_name, file_extension = os.path.splitext(teamprojectfile.name)
            file_name_upload = '{}{}'.format(original_name, file_extension)

            link = google_drive_upload(teamprojectfile)

            print "path: ", path
            print "link: ", link
            print "link: ", link['link']

            program_flow.team_project_slide_file = link['link']
            program_flow.team_project_slide_title = file_name_upload
            program_flow.team_project_slide_file_id = link['id']
            program_flow.team_project_talking_points = teamproject_text
            program_flow.number_of_teams = team_number
            program_flow.team_project_boolean = teamprojectpublic
            # program_flow.team_project_slide_type = link['type']
            program_flow.save()

            os.remove(link['remove'])
            print "preview: ",  link

        elif 'teampowerpointsubmit' in request.POST and request.FILES:
            print "teampowerpointsubmit: "
            teampowerpointfile = request.FILES.get('teampowerpointfile')
            teampowerpointpublic = request.POST.get('teampowerpointpublic')
            teampowerpoint_text = request.POST.get('teampowerpoint_text')

            path = save_file(teampowerpointfile)

            original_name, file_extension = os.path.splitext(teampowerpointfile.name)
            file_name_upload = '{}{}'.format(original_name, file_extension)

            link = google_drive_upload(teampowerpointfile)

            print "path: ", path
            print "link: ", link
            print "link: ", link['link']

            print "preview: ",  link
            program_flow.team_slideshow_slide_file = link['link']
            program_flow.team_slideshow_slide_title = file_name_upload
            program_flow.team_slideshow_slide_file_id = link['id']
            program_flow.team_slideshow_talking_points = teampowerpoint_text
            program_flow.team_slideshow_boolean = teampowerpointpublic
            # program_flow.team_slideshow_slide_type = link['type']
            program_flow.save()
            os.remove(link['remove'])

        elif 'judgingsubmit' in request.POST and request.FILES:
            print "judgingsubmit: "
            judgingfile = request.FILES.get('judgingfile')
            judgingpublic = request.POST.get('judgingpublic')
            judge_text = request.POST.get('judge_text')

            path = save_file(judgingfile)

            original_name, file_extension = os.path.splitext(judgingfile.name)
            file_name_upload = '{}{}'.format(original_name, file_extension)

            link = google_drive_upload(judgingfile)

            print "path: ", path
            print "link: ", link
            print "link: ", link['link']

            print "preview: ",  link
            program_flow.judges_slide_file = link['link']
            program_flow.judges_slide_title = file_name_upload
            program_flow.judges_slide_file_id = link['id']
            program_flow.judges_talking_points = judge_text
            program_flow.judges_boolean = judgingpublic
            program_flow.save()

            os.remove(link['remove'])

    return render(request, 'program_flow.html')


# def forgotpassword(request):
#
#     pass

# password reset form
import uuid
@csrf_exempt
def forgotpassword(request):
    email_reset = request.POST.get('email_reset')
    print "email_reset", email_reset

    # user = None
    try:
        user = User.objects.get(username__exact=email_reset)
    except Exception as e:
        print "e: ", e
        return HttpResponse('error')
    # send_mail()
    print "user email: ", user

    token = uuid.uuid1()
    user.userprofile.passwor_reset_token = token
    user.userprofile.save()
    result = send_email(sender="sender email address", subject="Forget Password.",
                      receive=user.email, name=user.first_name,  message='Please Click Below link to reset password',token=token )
    if result == 'success':
        return HttpResponse('success')
    else:
        return HttpResponse('error')



from email.header    import Header
from email.mime.text import MIMEText
from getpass         import getpass
from smtplib         import SMTP_SSL

from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string

def send_email(sender,subject, receive,name ,message,token ):
    top_content = None

    try:

        context_email = {
                'heading' : subject,
                'sub_heading' : top_content,
                'text' : "Please click on the link below to reset the password",
                'token':token,
                'name':name
            }
        print 'recieve: ', receive
        html_content = render_to_string('email_template.html', context_email)
        text_content = strip_tags(html_content)
        #
        # email = EmailMessage('Password Reset for knodemy',text_content , to=[receive])
        # email.attach_alternative(html_content, "text/html")
        # email.send()

        html_content = render_to_string('email_template.html', context_email)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, sender, [str(receive)])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print "email sent: ",receive
        return 'success'

    except Exception as e:
        print "e: ", e
        print "email not sent"

        return 'error'


def reset(request, token):
    print "request user; ", request.user
    print "token: ", token
    error = None
    user_token = None
    invalid = False
    context = None
    try:

        user_token = UserProfile.objects.get(passwor_reset_token=token)
        print "token: ", user_token.passwor_reset_token
        if request.method == 'POST':
            req = request.POST

            password = req['password1']
            confirm_password = req['password2']

            if user_token:
                user_token.user.set_password(password)
                user_token.user.save()
                return redirect('login')

            else:
                invalid = True
        context = {
            'name': user_token.user.first_name,
            'token': user_token.passwor_reset_token,
            'error': error,
            'invalid': invalid
        }
        print "context: ", context
    except Exception as e:
        print "e: ", e
        print "token not define"

    print "context1: ", context

    return render(request, 'password_reset/reset.html', context)