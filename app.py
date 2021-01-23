# Application that 
import os, sqlite3, json, hashlib, binascii, uuid
from flask import Flask, request, render_template



curr_dir = os.getcwd()
db_loc = os.path.join(curr_dir, "databass.db")
print("DB loc is {}".format(db_loc))
app = Flask(__name__)
app.secret_key=b'Kw\xc5\xac\x9e\x93\x8e\x82\xb8+Ot&U\xf4!'
uuid = uuid.uuid4().hex



def setup_db():
    try:
        conn = sqlite3.connect(db_loc)
        print("Created database file. Good")
        cur = conn.cursor()
        print("Connected successfully to {}.".format(db_loc))
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
                firstname text, lastname text, username text, email text, password blob
                )""")
        conn.commit()
        print("Created database structure. Good")
        conn.close()
        
    except sqlite3.Error as e: 
        print("Info: {}".format(e.args[0]))

def connect_db():
    try:
        conn = sqlite3.connect(db_loc)
        return conn
    except sqlite3.Error as e:
        print("Error connecting: {}".format(e.args[0]))

def write_stuff(inputdict, passwd):
    with connect_db() as conn:
        cur = conn.cursor()
        #print("Writing {} to database".format(inputdict))
        cur.execute("INSERT INTO users VALUES (?,?,?,?,?)", [inputdict['firstName'],\
            inputdict['lastName'], inputdict['username'], inputdict['email'], passwd])
        conn.commit()

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def check_user(username):
    try:
        if connect_db().cursor().execute("""select * FROM users
                                where username='{}'""".format(username)).fetchone():
            return True
    except sqlite3.Error as e:
        print(e)

def check_email(email):
        try:
            if connect_db().cursor().execute("""select * FROM users
                                where email='{}'""".format(email)).fetchone():
                return True
        except sqlite3.Error as e:
            print(e)

        
setup_db()
@app.route("/")
def index():
    
    return render_template("index.html", uuid=uuid)

@app.route("/", methods=['POST'])
def my_form_post():
    ''' Create a dict with keys from POST and their corresponding values
        then return a json of the results dict'''
    results = {}
    for key, value in request.form.items():
        results[key] = value
       # Check to see if username already exists 
    q = results['username']
    w = results['email']
   # res = connect_db()
    

    if check_user(q) and check_email(w):
        print("Username and email already exists.")
        return render_template('index.html', check_user=check_user(q), check_email=check_email(w))
    elif check_email(w):
        print("Email already exists.")
        return render_template('index.html', check_email=check_email(w))
    elif check_user(q):
        print("User already exists.")
        return render_template('index.html', check_user=check_user(q))
    else:
        hashedpasswd = hash_password(results['password'])
        write_stuff(results, hashedpasswd)
        wentwell = True
    
    return render_template('index.html', wentwell=wentwell)

@app.route("/index1.html", methods=['GET', 'POST'])
def hi():
        if request.method == 'POST':
            results = {}
            for key, value in request.form.items():
                results[key] = value
            q = results['username']
            p = results['password']
            res = connect_db()
            try:
                cur = res.cursor().execute("""select * FROM users
                                                   where username='{}'""".format(q))
            except sqlite3.Error as e:
                print(e)
            userinfo = cur.fetchall()
            hashedpasswd = userinfo[0][4]
            print(userinfo)
            if len(userinfo) > 0:
                givenpass = userinfo[0][1]  
                print(givenpass)
            else:
                wrongpass = True
                return render_template("index1.html", wrongpass = wrongpass)
            

            if userinfo and verify_password(hashedpasswd, p):
                print("Found data")
                notfound = False
                print(userinfo)
                firstname = userinfo[0][0]
                lastname = userinfo[0][1]
                username = userinfo[0][2]
                email = userinfo[0][3]
                print("Last name is {}".format(firstname))
                print("Last name is {}".format(lastname))
                print("Username is {}".format(username))
                print("Email is {}".format(email))
                return render_template("index1.html", username=username, firstname=firstname, lastname=lastname, email=email)
            if userinfo and not verify_password(givenpass, p):
                print("Found data but couldn't authenticate password :(")
                wrongpass = True
                return render_template("index1.html", wrongpass = wrongpass)
            else:
                print("Couldn't find that username")
                notfound = True
                return render_template("index1.html", notfound = notfound)
        
        if request.method == 'GET':
            return render_template("index1.html", uuid=uuid)

    




@app.route("/hi/<username>")
def greet(username):
    return("Hi there {}! How are you?".format(username))

if __name__ == "__main__":
    app.run(host='192.3.81.153', port=8000, debug=False)