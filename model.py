from utils import *
from google.appengine.ext import db
from google.appengine.api import memcache
import random
import hashlib
import logging


def article_key():
    return db.Key.from_path('Wiki', 'pages')

def users_key(group = 'default'):
    return db.Key.from_path('users', group)



class Users(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, uid):
        return Users.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = Users.all().filter('username =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return Users(parent = users_key(),
                    username = name,
                    password = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.password):
            return u


class Article(db.Model):
    username = db.StringProperty(required = True)
    title = db.StringProperty(required = True)
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_updated = db.DateTimeProperty(auto_now_add = True)
    version = db.IntegerProperty()

    @classmethod
    def by_username(cls, username):
        a = Article.all().filter('username =', username).get()
        return a

    @classmethod
    def by_title(cls, title):
        a = Article.all().filter('title =', title).order('-created').get()
        return a

    @classmethod
    def create_article(cls, username, title, content, version):
        return Article(parent = article_key(),
                       username = username,
                       title = title,
                       content = content,
                       version = version)


##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)
