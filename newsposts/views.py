from django.shortcuts import render
from django.http import HttpResponse,  Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse

from .models import Newspost, Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.conf import settings

import requests


# Static variables

google_captcha_url = 'https://www.google.com/recaptcha/api/siteverify'
google_captcha_key = settings.CAPTCHA_SERVER_KEY
default_group_name = settings.DEFAULT_GROUP_NAME


# Helper Functions

def make_post_request_json(go_url, data_dict):
    r = requests.post(go_url, data_dict)
    return r.json()


# Views here.

def home(request):
    context = {}
    try:
        context['latest_post_list'] = Newspost.objects.order_by('-pub_date')[:3]
    except:
        pass
    
    return render(request, 'index.html', context)

def about(request):
    context = {}
    try:
        context['admin_list'] = User.objects.filter(is_staff=True)
    except:
        pass

    return render(request, 'about.html', context)

def register_news(request):
    context = {'form_type': "Register"}
    if request.method == 'POST':
        # Validate Captcha and Form
        json = make_post_request_json(google_captcha_url, {'secret': google_captcha_key, 'response':request.POST['g-recaptcha-response'],})
        form_validity = UserCreationForm({'username': request.POST['username'], 'password1': request.POST['password1'], 'password2': request.POST['password2']}).is_valid()
        if json['success'] == True and form_validity:
            u = User.objects.create_user(request.POST['username'], '', request.POST['password1'] )
            try:
                g = Group.objects.get(name=default_group_name)
            except:
                # Group does not exist, create group and add permissions
                g = Group.objects.get_or_create(name=default_group_name)[0]
                p1 = Permission.objects.get(name='Can add comment')
                p2 = Permission.objects.get(name='Can view comment')
                p3 = Permission.objects.get(name='Can view post')
                p4 = Permission.objects.get(name='Can view newspost')
                g.permissions.set([p1, p2, p3, p4])
                context['error_message'] = "Your account may need further validation before full access"
            # Add resulting group to the user
            u.groups.add(g)
            print(u.groups)
        else:
            # Captcha or form validation failed
            context['error_message'] = "There was an issue with your request"
    # Return form with resulting error messages in context if any
    context['form'] = UserCreationForm()
    return render(request, 'registration/login.html', context)

def login_news(request):
    context = {'form_type': "Log In"}
    if request.method == 'POST':
        # Validate Captcha and Form
        json = make_post_request_json(google_captcha_url, {'secret': google_captcha_key, 'response':request.POST['g-recaptcha-response'],})
        if json['success'] == True:
            # I don't like this, data is pulled straight from post request
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)                
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect(reverse('newsposts:home'))
            else:
                # Return an 'invalid login' error message.
                context['error_message'] = 'Incorrect Username or Password'
        else:
            # This case if there is an issue with the robot check or form
            context['error_message'] = 'Issue with your request'
    context['form'] = AuthenticationForm()
    return render(request, 'registration/login.html', context)

def logout_news(request):
    # Log out user if they are logged in. Otherwiser redirect to home
    if request.user.is_authenticated:
        logout(request)
    
    return HttpResponseRedirect(reverse('newsposts:home')) 

@login_required
@permission_required('newsposts.view_newspost', raise_exception=True)
def posts(request):
    # Return a list of posts
    latest_post_list = get_list_or_404(Newspost.objects.order_by('-pub_date'))[:10]
    context = {'latest_post_list': latest_post_list}
    return render(request, 'newsposts.html', context)

@login_required
@permission_required('newsposts.view_newspost', raise_exception=True)
def post_specific(request, newspost_id):
    # View a specific post
    newspost = get_object_or_404(Newspost, pk=newspost_id)
    comment_list = list(newspost.comment_set.filter(approved_status=True).values())
    # Load comment Author objects for complete information
    for c in comment_list:
        c['comment_author_name'] = User.objects.get(pk=c['comment_author_id']).username
    context = {'p': newspost, 'comment_list': comment_list}
    return render(request, 'newspost_individual.html', context)

@login_required
@permission_required('newsposts.add_comment', raise_exception=True)
def post_comment(request, newspost_id):
    # Post a comment to a post
    if request.method == 'POST' and request.user.is_authenticated:
        # Verify Captcha
        json = make_post_request_json(google_captcha_url, {'secret': google_captcha_key, 'response':request.POST['g-recaptcha-response']})
        if json['success'] == True:
            newspost = get_object_or_404(Newspost, pk=newspost_id)
            comment = Comment(newspost_parent=newspost, comment_text=request.POST['comment_text'], pub_date=timezone.now(), comment_author=request.user)
            comment.save()
        
    return HttpResponseRedirect(reverse('newsposts:posts_individual', args=(newspost_id,)))
