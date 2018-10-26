from flask import Flask, render_template, flash, redirect, url_for, logging, request,session
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


#entry file that leads the app
app = Flask(__name__) # init a flask instance
Articles = Articles()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2220289jj'
app.config['MYSQL_DB'] = 'mypages'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' #call excute() to excute query

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)

@app.route('/articles/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', validators=[validators.length(min=1,max=50)])
    username = StringField('Username', validators=[validators.length(min=4, max=25)])
    email = StringField('Email', validators=[validators.length(min=6, max=50)])
    password = PasswordField('Passward', validators = [
        validators.data_required(),
        validators.EqualTo('confirm',message='Passward do not match')
    ])
    confirm = PasswordField('Confirm Passward')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate(): #form is submitted
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, passward) values(%s, %s, %s, %s)", (name,email,username,password))
        mysql.connection.commit()

        cur.close()

        flash('You are now registered and can log in', 'success')
        redirect(url_for('index'))
    return render_template('register.html',form = form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['passward']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#Dashboard
#TODO




if __name__ == "__main__":
    app.secret_key = 'mypages'
    app.run(debug=True) #open debug mode so you do not need to reopen the app when you make a change