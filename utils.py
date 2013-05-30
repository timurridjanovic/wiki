import hmac
import re
from string import letters
from model import *
import logging

SECRET = 'Timur'
def hash_str(s):
    return hmac.new(SECRET, str(s)).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)


##### time zone stuff



##### memcache stuff

def update_memcache(key, cache):
    old_cache = memcache.get(key)
    cache = old_cache + cache
    memcache.set(key, cache)
    new_cache = memcache.get(key)
    return new_cache

