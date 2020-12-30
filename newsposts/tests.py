from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from .models import Newspost, Comment
from django.contrib.auth.models import User, Group, Permission, AnonymousUser
from django.utils import timezone
from .views import posts
from django.conf import settings

settings.DEBUG = False
 
# Create your tests here.

def create_post(post_title, post_text):
    """
    Create a post with the given `post_title` and `post_text`
    """
    return Newspost.objects.create(newspost_title_text=post_title, newspost_main_text=post_text, pub_date=timezone.now())

def create_comment(newspost_parent, comment_text):
    """
    Create a comment with the given `comment_title` and `comment_text`
    """
    return Comment.objects.create(newspost_parent=newspost_parent, comment_text=comment_text, pub_date=timezone.now())

def create_user(username, password, test_email=''):
    """
    Create a user with a username and password then login
    """
    u = User.objects.create_user(username=username, email=test_email, password=password)
    g = Group.objects.get_or_create(name='test_Average')[0]
    p1 = Permission.objects.get(name='Can add comment')
    p2 = Permission.objects.get(name='Can view comment')
    p3 = Permission.objects.get(name='Can view newspost')
    g.permissions.set([p1, p2, p3])
    u.groups.add(g)
    return u

def login_user(case, user):
    case.force_login(user)

def create_super_user(username, password, test_email=''):
    """
    Create a user with a username and password
    """
    return User.objects.create_super_user(username=username, email=test_email, password=password)

class NewspostsHomeViewTests(TestCase):
    def test_no_posts(self):
        """
        If no posts exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('newsposts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No posts are available.")
        self.assertQuerysetEqual(response.context['latest_post_list'], [])

    def test_with_posts(self):
        """
        If posts exist, posts are displayed in response and else message does not appear
        """
        post_title = 'Test Post In Tests'
        post_text = 'SUPER COOL TEXT IN TEST'
        create_post(post_title, post_text)
        response = self.client.get(reverse('newsposts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post In Tests')
        self.assertQuerysetEqual(response.context['latest_post_list'], ['<Newspost: ' + post_title + '>'])
        self.assertNotContains(response, 'No posts are available.')

class NewpostsPostsLoggedIn(TestCase):
    def setUp(self):
        # Set up user and access
        u = create_user('boozle', 'asdf@1234')
        self.factory = RequestFactory()
        self.user = u

    def test_posts_access_no_posts(self):
        """
        If user is logged in, ensure default access to page
        Throws 404 with no posts
        """
        self.client.force_login(self.user)
        request = self.client.get(reverse('newsposts:posts'))
        self.assertEqual(request.status_code, 404)
    
    def test_posts_access_with_posts(self):
        """
        If user is logged in, ensure default access to page
        """
        # Dummy Post
        post_title = 'Posts View Access Title'
        post_text = 'Posts View Access Text'
        create_post(post_title, post_text)

        self.client.force_login(self.user)
        request = self.client.get(reverse('newsposts:posts'))
        self.assertEqual(request.status_code, 200)

    def test_with_posts(self):
        """
        If posts exist and logged in, show posts
        """
        # Dummy Post
        post_title = 'Posts View Tests 002'
        post_text = 'Posts View Tests Text 002'
        create_post(post_title, post_text)

        self.client.force_login(self.user)
        request = self.client.get(reverse('newsposts:posts'))
        self.assertEqual(request.status_code, 200)

class NewspostsPostsViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_access_posts(self):
        """
        If not logged in, login redirect
        """
        response = self.client.get(reverse('newsposts:posts'))
        self.assertEqual(response.status_code, 302)

class NewspostsIndividualPostsViewTests(TestCase):
    def setUp(self):
        self.user = create_user('boozle', 'asdf@1234')

    def test_no_posts(self):
        """
        if no post exists, throw 404
        """
        # Request
        self.client.force_login(self.user)
        response = self.client.get(reverse('newsposts:posts_individual', args=(1,)))
        
        self.assertEqual(response.status_code, 404)

    def test_with_posts(self):
        """
        If post exists, ensure display of post
        """
        # Dummy Post
        post_title = "Individual Test 002"
        post_text = "Individual Test Text 002"
        test_my_post = create_post(post_title, post_text)
        
        # Request
        self.client.force_login(self.user)
        response = self.client.get(reverse('newsposts:posts_individual', args=(test_my_post.id,)))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post_text)
        self.assertEqual(response.context['p'], test_my_post )
        

    def test_posts_no_comments(self):
        """
        If post exists with no comments ensure message appears
        """
        # Dummy Post
        post_title = "Individual Test 003"
        post_text = "Individual Test Text 003"
        test_my_post = create_post(post_title, post_text)
        
        # Request
        self.client.force_login(self.user)
        response = self.client.get(reverse('newsposts:posts_individual', args=(test_my_post.id,)))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Comments yet...")

    def test_post_with_comments(self):
        """
        If post exists with comments, ensure comments display
        """
        # Dummy Data
        post_title = "Individual Test 003"
        post_text = "Individual Test Text 003"
        test_my_post = create_post(post_title, post_text)
        comment_text = "Individual Comment Text 003"
        test_comment = create_comment(test_my_post, comment_text)
        test_comment.approved_status = True
        test_username = "bartolo"
        test_email = "asdf@email.com"
        test_pass = "nothing!"
        test_comment.comment_author = create_user(test_username, test_pass, test_email)
        test_comment.save()
        
        # Request
        self.client.force_login(self.user)
        response = self.client.get(reverse('newsposts:posts_individual', args=(test_my_post.id,)))
        
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No Comments yet...")
        self.assertContains(response, test_comment.comment_text)
        