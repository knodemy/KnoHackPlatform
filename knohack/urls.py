"""knohack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from knohack import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from hackathon import views as hackathon_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',  hackathon_views.index, name="index"),
    url(r'^adminindex/$',  hackathon_views.admin_index, name="admin_index"),
    url(r'^login/$', hackathon_views.custom_user_login, name="login"),
    url(r'^logout/$', hackathon_views.logout_user, name="logout_user"),
    url(r'^adminregister/$', hackathon_views.register_user_admin, name="admin_register"),
    url(r'^admindashboard/$', hackathon_views.admin_dashboard, name="admin_dashboard"),
    url(r'^createevent/$', hackathon_views.create_event, name="create_event"),
    url(r'^editevent/(?P<id>[^\.]+)/$', hackathon_views.edit_event, name="edit_event"),
    url(r'^programflow/(?P<id>[^\.]+)/$', hackathon_views.program_flow, name="program_flow"),
    url(r'^eventlist/$', hackathon_views.event_list, name="event_list"),
    url(r'^manage/$', hackathon_views.manage_events, name="manage_events"),
    url(r'^knohackeventlogin/(?P<id>[^\.]+)/$', hackathon_views.knohack_event_login, name="knohack_event_login"),
    url(r'^eventregistration/(?P<id>[^\.]+)/$', hackathon_views.registration_for_event, name="registration_for_event"),
    url(r'^eventdelete/(?P<id>[^\.]+)/$', hackathon_views.event_delete, name="event_delete"),
    url(r'^eventdetail/(?P<id>[^\.]+)/$', hackathon_views.event_detail, name="event_detail"),
    url(r'^studentregister/$', hackathon_views.register_user_student, name="student_register"),
    url(r'^studentdashboard/$', hackathon_views.student_dashboard, name="student_dashboard"),
    url(r'^shareflyer/$', hackathon_views.share_flyer, name="share_flyer"),
    url(r'^studentprofile/$', hackathon_views.student_profile, name="student_profile"),
    url(r'^studentdetail/(?P<id>[^\.]+)/$', hackathon_views.student_detail, name="student_detail"),
    url(r'^eventprofile/(?P<id>[^\.]+)/$', hackathon_views.event_profile, name="event_profile"),
    url(r'^adminprofile/$', hackathon_views.admin_profile, name="admin_profile"),
    url(r'^howitwork/$', hackathon_views.how_it_work, name="how_it_work"),
    url(r'^attendeeslist/(?P<id>[^\.]+)/$', hackathon_views.student_attendees_list, name="student_attendees_list"),
    url(r'^studentflow/(?P<id>[^\.]+)/$', hackathon_views.student_flow, name="student_flow"),
    url(r'^uploadfile/$', hackathon_views.upload_file, name="upload_file"),
    url(r'^list/$', hackathon_views.files_list, name="files_list"),
    url(r'^createteam/$', hackathon_views.create_team, name="create_team"),
    url(r'^studentevents/$', hackathon_views.student_events, name="student_events"),

    url(r'^student_team_list/$', hackathon_views.student_team_list, name="student_team_list"),

    url(r'^forgotpassword/$', hackathon_views.forgotpassword, name='forgotpassword'),
    url(r'^reset/(?P<token>.+)/', hackathon_views.reset, name='reset'),

    # default pages urls with bases
    url(r'^login_default/$', hackathon_views.login_default, name="login_default"),
    url(r'^admin_default_page/$', hackathon_views.admin_default_page, name="admin_default_page"),

    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT} )
]

