import webapp2
import os
import jinja2
from model import *
from utils import *
import logging

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)



class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)


    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and Users.by_id(int(uid))



class Signup(Handler):
    def get(self):
        if self.user:
            self.render('signup.html', user = self.user, username = self.user.username)
        else:
            self.render('signup.html')
   


    def post(self):
        have_error = False
        have_user = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        params = dict(username=self.username, email=self.email)

        
        users = Users.all()
        if users.filter("username =", self.username).get():
            have_error = True
            params['user_exists_error'] = "This user is already registered!"  


        if not valid_username(self.username):
            params['username_error'] = "You have not entered a valid username!"
            have_error = True
        
        if not valid_password(self.password):
            params['password_error'] = "You have not entered a valid password!"
            have_error = True
        elif self.verify != self.password:
            params['verify_error'] = "Your passwords didn't match!"
            have_error = True

        if not valid_email(self.email):
            params['email_error'] = "You have not entered a valid email!"
            have_error = True

        if have_error:
            self.render("signup.html", **params)
        else:
  
            u = Users.register(self.username, self.password, self.email)
            key = u.put()
            self.login(u)
            
            self.redirect("/")


class Login(Handler):
    def get(self):
        if self.user:
            self.render('login.html', user = self.user, username = self.user.username)
        else:
            self.render('login.html')


    def post(self):
        username = self.request.get("login_username")
        password = self.request.get("login_password")
        
        u = Users.login(username, password)
        if u:
            self.login(u)
            self.redirect("/")
        else:
            msg = "Invalid login"
            self.render("login.html", login_error = msg)


class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/')    


class Search(Handler):
    def get(self):
        self.redirect('/')

    def post(self):
        search = self.request.get("search")
        self.redirect('/%s' % search)

