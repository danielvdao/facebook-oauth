from flask import Flask, redirect, url_for, session, request,g
from flask_oauth import OAuth
import urllib2, httplib2
from facepy import GraphAPI

"""
        Flask seems to have a pretty nice Oauth library. I found some of this online and tweaked around with it, using my own app id, secret, and whatnot.
So what this essentially does is set up a host at localhost:5000 and with that 
it will ask you to login first. Once you login, you'll be asked for application
permissions. Currently I have added developers to the app, and they are able to
test the app and post statuses. Sadly this can't go towards all users yet because I need the permission from Facebook.

        I'm also using a nice library called facepy to update user statuses.
        Located at: http://facepy.readthedocs.org/en/latest/

"""

# Set up variables  #
SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '1447148262225323'
FACEBOOK_APP_SECRET = '3a9e8151d533e04e88df1a74d43ef97c'
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
app.testing = True
"""
The OAuth object is a registry for remote applications. It helps to provide for OAuth
"""
oauth = OAuth()

"""
        request_token_url - URL for requesting new tokens
        access_token_url - URL for token exchange
        consumer_key - app id
        consumer_secret - app secret
        request_token_params - the scope of our permissions
 
        Note: For Facebook you don't use request_token_url, however you 
        need to provide a scope of permissions.
"""
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email, publish_actions'}
)


@app.route('/')
def index():
    return redirect(url_for('login'))


"""
Calls authorize and passes to the endpoint the user should be directed to,
In this case it's /login/authorized. You will see the variable next_url. Essentially 
it just redirects the user after a successful login. 
"""

@app.route('/login')
def login():
    print 'hello world!'
    url_next = 'test'
    return facebook.authorize(callback=url_for('facebook_authorized',
    next=url_next,
    _external=True))


"""
So when you call facebook.authorize in the login function, what will happen is the sign in screen will pop up and ask for your information. You can then 
choose whether or not to accept the application.
If you deny, then the resp object (response object) will be none => access denied. Probably a good time
to put a 404 error or something of that sort.   
"""
@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'User has denied request'
    session['oauth_token'] = (resp['access_token'], '')
    acc_token =  str(resp['access_token'])
    graph = GraphAPI(acc_token)
    return 'made it to login!'
                                           
"""
This is my test function. After you login, try going to localhost:5000/test
The idea was to simulate a share button, as if once a user clicks then they'll
have posted a status. I don't think this will work for you however, since you are not a developer on my my facebook app. If you would like to be a developer let me know and I can add you. 

"""
@app.route('/test')
def test():
    graph = GraphAPI(str(session['oauth_token'][0]))
    graph.post('me/feed',message='Hello World!')
    return 'post worked'


"""
Has the users token and token secret
"""
@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


if __name__ == '__main__':
    app.run()

