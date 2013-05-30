import time
import logging
import json
from utils import *
from controller import *
from model import *



class Page(Handler):
    def get(self, page=''):
        #db.delete(db.Query())
        #memcache.flush_all()
        title = page
        logging.error(title)
        if page=='':
            title = "Welcome"
        content = memcache.get(title)
        if not content:
            logging.error("DB hit: %s" % title)
            content = Article.by_title(title)
            if content:
                content=content.content
            memcache.set(title, content)
        if self.user:
            if content:
                self.render('page.html', user = self.user, username = self.user.username, page=page, content=content, title=title)
            else:
                self.redirect('/_edit/%s' % page)
        else:
            if content:
                self.render('page.html', page=page, content=content, title=title)
            else:
                self.render('page.html', page=page, title=title)


    def post(self, page=''):
        content = self.request.get("content")
        username = self.user.username
        title = page
        ###database push
        if page == '':
            title = 'Welcome'
        a = Article.create_article(username, title, content)
        a.put()
     
        
        ###memcache push
        memcache.set('last_page', title)
        memcache.set(title, content)
        self.redirect("/%s" % page)

class Edit(Handler):
    def get(self, page=''):
        title = page
        if page == '':
            title = "Welcome"
        if self.user:
            content = memcache.get(title)
            if content:
                self.render('edit.html', user = self.user, username = self.user.username, page=page, content=content, title=title)
            else:
                if page == '':
                    title = "Welcome"
                self.render('edit.html', user = self.user, username = self.user.username, page=page, title=title)
        else:
            self.redirect('/login')

    def post(self, page=''):
        content = self.request.get("content")
        username = self.user.username
        title = page
        ###database push
        if page == '':
            title = "Welcome"
        if content == '':
            error = 'We need some content!'
            self.render('edit.html', user = self.user, username = self.user.username, page=page, title=title, error=error)
        else:

            version = increment_version(page)
            a = Article.create_article(username, title, content, version)
            a.put()
     
            logging.error(content)
            logging.error(username)
            logging.error(title)
            ###memcache push
            memcache.set('last_page', title)
            memcache.set(title, content)

            ###update history memcache
            update_history = memcache.get(page+'_history')
            if update_history:

                update_history.insert(0, a)
                memcache.set(page+'_history', update_history)
            self.redirect("/%s" % page)
            

class History(Handler):
    def get(self, page=''):
        title = page
        logging.error(page)
        if page == '':
            title = "Welcome"
        articles = memcache.get(page+'_history')
        if not articles:    
            articles = Article.all().filter('title =', title).order('-created')
            logging.error('db hit history')
            articles = list(articles)
            memcache.set(page+'_history', articles)
        if self.user:
            self.render('history.html', user = self.user, username = self.user.username, title=title, articles=articles, page=page)
        else:
            self.redirect('/login')
       


    def post(self, page=''):
        title = page
        content = self.request.get("article_content")
        if page == '':
            title = "Welcome"
        memcache.set(title+'view', content)
        if 'edit' in self.request.POST:
            self.redirect('/view/_edit/%s' % page)
        if 'view' in self.request.POST:
            self.redirect('/view/%s' % page)

##### to increment the version of the article and push it in the database. The higher the version, the more recent the article.
def increment_version(page):
    version = memcache.get('version%s' % page)
    if not version:
        logging.error('db hit version')
        version = Article.all().filter('title =', page).order('-created').get()
        if version:
            version = version.version
        
        else:
            version = 0
    version += 1
    memcache.set('version%s' % page, version)
    return version


class View(Handler):
    def get(self, page=''):
        title = page
        if page=='':
            title = "Welcome"
        content = memcache.get(title+'view')
        if self.user:
            if content:
                self.render('view.html', user = self.user, username = self.user.username, page=page, content=content, title=title)
            else:
                self.redirect('/_edit/%s' % page)
        else:
            if content:
                self.render('view.html', page=page, content=content, title=title)
            else:
                self.render('view.html', page=page, title=title)


    def post(self, page=''):
        content = self.request.get("content")
        username = self.user.username
        title = page
        ###database push
        if page == '':
            title = 'Welcome'
        a = Article.create_article(username, title, content)
        a.put()
     
        
        ###memcache push
        memcache.set('last_page', title)
        memcache.set(title, content)
        self.redirect("/%s" % page)



class ViewEdit(Handler):
    def get(self, page=''):
        title = page
        if page == '':
            title = "Welcome"
        if self.user:
            content = memcache.get(title+'view')
            if content:
                self.render('viewedit.html', user = self.user, username = self.user.username, page=page, content=content, title=title)
            else:
                if page == '':
                    title = "Welcome"
                self.render('viewedit.html', user = self.user, username = self.user.username, page=page, title=title)
        else:
            self.redirect('/login')

    def post(self, page=''):
        content = self.request.get("content")
        username = self.user.username
        title = page
        ###database push
        if page == '':
            title = "Welcome"
        if content == '':
            error = 'We need some content!'
            self.render('viewedit.html', user = self.user, username = self.user.username, page=page, title=title, error=error)
        else:

            version = increment_version(page)
            a = Article.create_article(username, title, content, version)
            a.put()
     
            logging.error(content)
            logging.error(username)
            logging.error(title)
            ###memcache push
            memcache.set('last_page', title)
            memcache.set(title, content)

            ###update history memcache
            update_history = memcache.get(page+'_history')
            update_history.insert(0, a)
            memcache.set(page+'_history', update_history)
            self.redirect("/%s" % page)
            
           

app = webapp2.WSGIApplication([('/', Page), ('/signup', Signup), ('/login', Login), ('/logout', Logout), ('/search', Search), ('/(?!search|login|signup|logout|_edit|history|_history|view)(\w+)/?', Page), ('/_edit/(\w+)/?', Edit), ('/_edit/', Edit), ('/_history/(\w+)/?', History), ('/_history/', History), ('/view/(?!_edit)(\w+)/?', View), ('/view/', View), ('/view/_edit/(\w+)/?', ViewEdit), ('/view/_edit/', ViewEdit)], 
		debug=True)

