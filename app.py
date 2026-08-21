from flask import *
import sys
import logging
from interfaces.databaseinterface import Database
from interfaces.hashing import *

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
app.config['SECRET_KEY'] = "Type in secret line of text"

DATABASE = Database("database/test.db", app.logger)

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/')
def redirect_to_login():
    return redirect('./login')
@app.route('/logout')
def logout():
    app.logger.info("Log out")
    session.clear()
    return redirect('./login')

@app.route('/admin', methods=["GET","POST"])
def admin():
    
    if 'permission' not in session:
        return redirect("./")
    
    if request.method == "POST":
        selectedusers = request.form.getlist("selectedusers")
        for userid in selectedusers:
            if int(userid) != 1:
                DATABASE.ModifyQuery("DELETE FROM users WHERE userid = ?", (userid,))
        return redirect("./admin")

    app.logger.info("Admin")
    users = DATABASE.ViewQuery("SELECT userid, firstname, lastname, email, permission FROM users") or []
    return render_template("admin.html", users=users)

@app.route('/login', methods=["GET", "POST"])
def login():
    app.logger.info("Login page accessed")

    # Check if already logged in
    if 'userid' in session:
        if 'permission' in session:
            return redirect(url_for('admin'))
        return redirect(url_for('home'))

    message = "Please login"
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        if results:
            userdetails = results[0] 
            
            # Print to terminal to verify exact dictionary key names
            print("User details from DB:", userdetails) 

            if check_password(userdetails['password'], password):
                # Ensure keys match your database column names exactly
                session['userid'] = userdetails['userid'] 
                session['permission'] = userdetails['permission']
                session['name'] = f"{userdetails['firstname']} {userdetails['lastname']}"

                if 'permission' in session:
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('home'))
            else: 
                message = "Password incorrect"
        else:
            message = "User does not exist"

    return render_template("login.html", message=message)


@app.route('/home')
def home():
    # Verify the user has an active session
    if 'userid' not in session:
        return redirect(url_for('login'))

    app.logger.info("Home page accessed")
    return render_template("home.html")

@app.route('/register', methods=['GET','POST'])
def register():
    app.logger.info("Register")
    message = "Please register"
    if request.method == "POST":

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        passwordconfirm = request.form['confirm_password']
        email = request.form['email']

        if password != passwordconfirm:
            message = "Error, passwords do not match"
        else:
            results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
            if results:
                message = "Error, user already exists"
            else:
                password = hash_password(password)
                DATABASE.ModifyQuery("INSERT INTO users (firstname, lastname, email, password) VALUES (?,?,?,?)", (firstname, lastname, email, password))
                message = "Success, users has been added"
                return redirect('./login')

    return render_template("register.html", message=message)

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000