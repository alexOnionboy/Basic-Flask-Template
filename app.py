from flask import *
import sys
import logging
from interfaces.databaseinterface import Database

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
DATABASE = Database('test.db', log=app.logger)




#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    message = "Please login to continue."
    if request.method == 'POST':
        email = request.form.get('email') #name of the input
        password = request.form.get('password') #name of input
        if email == 'admin' and password == 'admin':
            session['permission'] = 'admin'
            return redirect('/home')
        else:
            message="Invalid credentials. Please try again."
    app.logger.info("Login")
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    app.logger.info("Logout")
    session.clear()
    return redirect('/login')

@app.route('/register')
def register():
    app.logger.info("Register")
    return "Registration Page"

@app.route('/home')
def home():
    app.logger.info("Home")
    return "Home"

@app.route('/admin')
def admin():
    app.logger.info("admin")
    return "Admin"




#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
