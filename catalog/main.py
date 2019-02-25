from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, BykeCompanyName, BykeName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

# to connect database

engine = create_engine('sqlite:///bykes.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Bykes Store"

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
bykes_cat = session.query(BykeCompanyName).all()


# User login
@app.route('/login')
def showLogin():  
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    bykes_cat = session.query(BykeCompanyName).all()
    bm = session.query(BykeName).all()
    return render_template('login.html',
                           STATE=state, bykes_cat=bykes_cat, bm=bm)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(User1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Uet user information
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# get user email address
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

# Home


@app.route('/')
@app.route('/home')
def home():
    bykes_cat = session.query(BykeCompanyName).all()
    return render_template('myhome.html', bykes_cat=bykes_cat)


# Byke Category for admins


@app.route('/BykeStore')
def BykeStore():
    try:
        if login_session['username']:
            name = login_session['username']
            bykes_cat = session.query(BykeCompanyName).all()
            bc = session.query(BykeCompanyName).all()
            bm = session.query(BykeName).all()
            return render_template('myhome.html', bykes_cat=bykes_cat,
                                   bc=bc, bm=bm, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing bykes based on byke category


@app.route('/BykeStore/<int:bcid>/AllCompanys')
def showBykes(bcid):
    bykes_cat = session.query(BykeCompanyName).all()
    bc = session.query(BykeCompanyName).filter_by(id=bcid).one()
    bm = session.query(BykeName).filter_by(bykecompanynameid=bcid).all()
    try:
        if login_session['username']:
            return render_template('showBykes.html', bykes_cat=bykes_cat,
                                   bc=bc, bm=bm,
                                   uname=login_session['username'])
    except:
        return render_template('showBykes.html',
                               bykes_cat=bykes_cat, bc=bc, bm=bm)


# Add New Byke


@app.route('/BykeStore/addBykeCompany', methods=['POST', 'GET'])
def addBykeCompany():
    if request.method == 'POST':
        company = BykeCompanyName(name=request.form['name'],
                                  user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('BykeStore'))
    else:
        return render_template('addBykeCompany.html', bykes_cat=bykes_cat)


# Edit Byke Category


@app.route('/BykeStore/<int:bcid>/edit', methods=['POST', 'GET'])
def editBykeCategory(bcid):
    editedByke = session.query(BykeCompanyName).filter_by(id=bcid).one()
    creator = getUserInfo(editedByke.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Byke Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('BykeStore'))
    if request.method == "POST":
        if request.form['name']:
            editedByke.name = request.form['name']
        session.add(editedByke)
        session.commit()
        flash("Byke Category Edited Successfully")
        return redirect(url_for('BykeStore'))
    else:
        # bykes_cat is global variable we can them in entire application
        return render_template('editBykeCategory.html',
                               tb=editedByke, bykes_cat=bykes_cat)


# Delete Byke Category

@app.route('/BykeStore/<int:bcid>/delete', methods=['POST', 'GET'])
def deleteBykeCategory(bcid):
    tb = session.query(BykeCompanyName).filter_by(id=bcid).one()
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Byke Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('BykekStore'))
    if request.method == "POST":
        session.delete(tb)
        session.commit()
        flash("Byke Category Deleted Successfully")
        return redirect(url_for('BykeStore'))
    else:
        return render_template('deleteBykeCategory.html', tb=tb, 
                               bykes_cat=bykes_cat)


# Add New Byke Model Name Details


@app.route('/BykeStore/addCompany/addBykeDetails/<string:bcname>/add',
           methods=['GET', 'POST'])
def addBykeDetails(bcname):
    bc = session.query(BykeCompanyName).filter_by(name=bcname).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(bc.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Byke edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showBykes', bcid=bc.id))
    if request.method == 'POST':
        name = request.form['name']
        year = request.form['year']
        color = request.form['color']
        cc = request.form['cc']
        price = request.form['price']
        byketype = request.form['byketype']
        bykedetails = BykeName(name=name, year=year,
                               color=color, cc=cc,
                               price=price,
                               byketype=byketype,
                               date=datetime.datetime.now(),
                               bykecompanynameid=bc.id,
                               user_id=login_session['user_id'])
        session.add(bykedetails)
        session.commit()
        return redirect(url_for('showBykes', bcid=bc.id))
    else:
        return render_template('addBykeDetails.html',
                               bcname=bc.name, bykes_cat=bykes_cat)


# Edit Byke Model details


@app.route('/BykeStore/<int:bcid>/<string:bcmname>/edit',
           methods=['GET', 'POST'])
def editByke(bcid, bcmname):
    tb = session.query(BykeCompanyName).filter_by(id=bcid).one()
    bykedetails = session.query(BykeName).filter_by(name=bcmname).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this Byke edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showBykes', bcid=tb.id))
    # POST methods
    if request.method == 'POST':
        bykedetails.name = request.form['name']
        bykedetails.year = request.form['year']
        bykedetails.color = request.form['color']
        bykedetails.cc = request.form['cc']
        bykedetails.price = request.form['price']
        bykedetails.byketype = request.form['byketype']
        bykedetails.date = datetime.datetime.now()
        session.add(bykedetails)
        session.commit()
        flash("Byke Edited Successfully")
        return redirect(url_for('showBykes', bcid=bcid))
    else:
        return render_template('editByke.html',
                               bcid=bcid, bykedetails=bykedetails,
                               bykes_cat=bykes_cat)


# Delte Byke Model


@app.route('/BykekStore/<int:bcid>/<string:bcmname>/delete',
           methods=['GET', 'POST'])
def deleteByke(bcid, bcmname):
    tb = session.query(BykeCompanyName).filter_by(id=bcid).one()
    bykedetails = session.query(BykeName).filter_by(name=bcmname).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this Byke edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showBykes', bcid=tb.id))
    if request.method == "POST":
        session.delete(bykedetails)
        session.commit()
        flash("Deleted Byke Successfully")
        return redirect(url_for('showBykes', bcid=bcid))
    else:
        return render_template('deleteByke.html',
                               bcid=bcid, bykedetails=bykedetails, 
                               bykes_cat=bykes_cat)


# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None, headers={'content-type':
                  'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully '
                                 'disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json


@app.route('/BykeStore/JSON')
def allBykesJSON():
    bykecategories = session.query(BykeCompanyName).all()
    category_dict = [c.serialize for c in bykecategories]
    for c in range(len(category_dict)):
        bykes = [i.serialize for i in session.query(
                 BykeName).filter_by(
                     bykecompanynameid=category_dict[c]["id"]).all()]
        if bykes:
            category_dict[c]["byke"] = bykes
    return jsonify(BykeCompanyName=category_dict)

####


@app.route('/bykeStore/bykeCategories/JSON')
def categoriesJSON():
    bykes = session.query(BykeCompanyName).all()
    return jsonify(bykeCategories=[c.serialize for c in bykes])

####


@app.route('/bykeStore/bykes/JSON')
def itemsJSON():
    items = session.query(BykeName).all()
    return jsonify(bykes=[i.serialize for i in items])

#####


@app.route('/bykeStore/<path:byke_name>/bykes/JSON')
def categoryItemsJSON(byke_name):
    bykeCategory = session.query(
        BykeCompanyName).filter_by(name=byke_name).one()
    bykes = session.query(BykeName).filter_by(bykename=bykeCategory).all()
    return jsonify(bykeEdtion=[i.serialize for i in bykes])

#####


@app.route('/bykeStore/<path:byke_name>/<path:edition_name>/JSON')
def ItemJSON(byke_name, edition_name):
    bykeCategory = session.query(
        BykeCompanyName).filter_by(name=byke_name).one()
    bykeEdition = session.query(BykeName).filter_by(
           name=edition_name, bykename=bykeCategory).one()
    return jsonify(bykeEdition=[bykeEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
