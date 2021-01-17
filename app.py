from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user
from flask import current_app, render_template
from flask import Flask, session, redirect, url_for, escape, request
import os

from flask import current_app, render_template,request,redirect,url_for, abort
from flask_mysqldb import MySQL

class Database:
    def __init__(self):
        print("created")
    def add_post(self, title, content):
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute("INSERT INTO posts (Title, Content, School_id, Author_id, StudentNumber) VALUES (%s, %s, %s, %s, %s)",(title, content, 2,3,40))
        db.connection.commit()
        cur.execute(''' SELECT *  FROM posts ORDER BY Post_id DESC LIMIT 1''')
        data = cur.fetchall()
    def get_posts(self):
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute(''' SELECT posts.Title, posts.Content, schools.School_name, posts.Author_id, posts.StudentNumber, posts.Post_id   FROM posts JOIN schools ON schools.School_id = posts.School_id ORDER BY Post_id DESC''')
        data = cur.fetchall()
        ar = []
        for i in data:
            print(i[3])
            cur.execute("SELECT teacher.First_name FROM teacher WHERE teacher.Teacher_id= %s LIMIT 1"%(i[3]))
            a = cur.fetchall()
            ar.append([i[0], i[1], i[2], a[0][0], i[4], i[5]])
        return ar
    def insert_user(self, title, content, School_id, Author_id, StudentNumber):
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute("INSERT INTO posts (Title, Content, School_id, Author_id, StudentNumber) VALUES (%s, %s, %s, %s, %s)",(title, content, 2,3,40))
        db.connection.commit()
    def get_post(self, id):
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute((''' SELECT posts.Post_id, posts.Title, posts.Content, schools.School_name, posts.Author_id, posts.StudentNumber, school_address.School_Address, school_address.School_City, school_address.School_District   FROM posts JOIN schools ON schools.School_id = posts.School_id JOIN school_address ON school_address.School_Address=schools.School_Address WHERE posts.Post_id= %s''' % (id)))
        #cur.execute("SELECT * FROM posts WHERE Post_id= %s" % (id))
        data = cur.fetchall()[0]
        #Needs
        cur.execute("SELECT item_names.Item_name FROM posts JOIN needs ON needs.Post_id = posts.Post_id JOIN item_names ON item_names.Item_id = needs.Material_id  WHERE posts.Post_id= %s" % (id))
        needs = cur.fetchall()
        a = [data, needs]
        return a
    def new_post(self, form_title, form_content, school,num_students,needs,user_id):
        db = current_app.config["db"]
        cur = db.connection.cursor()

        
        cur.execute("SELECT  schools.School_name, schools.School_id   FROM schools JOIN school_address ON schools.School_Address = school_address.School_Address WHERE schools.School_name LIKE %s",("%"+school+"%",))
        data = cur.fetchall()
        if len(data)<2:
            return 0
        # school information
        cur.execute("SELECT  schools.School_name, schools.School_id   FROM schools JOIN school_address ON schools.School_Address = school_address.School_Address WHERE schools.School_name LIKE %s LIMIT 1",("%"+school+"%",))
        data = cur.fetchall()
        school_id = data[0][1]

        #insert new post 
        cur.execute("INSERT INTO posts (Title, Content, School_id, Author_id, StudentNumber) VALUES (%s, %s, %s, %s, %s)",(form_title, form_content, school_id,user_id,num_students))
        db.connection.commit()
        
        #Post id
        cur.execute(''' SELECT *  FROM posts ORDER BY Post_id DESC LIMIT 1''')
        data = cur.fetchall()
        
        post_id = data[0][0]

        #Needs
        for i in needs:
            cur.execute(" SELECT b.Item_id FROM item_names AS b WHERE b.Item_name = "+"'"+ i +"'")
            data = cur.fetchall()
            need_id = data[0][0]
            cur.execute("INSERT INTO needs (Post_id, Material_id) VALUES (%s,%s)",(post_id,need_id))

        db.connection.commit()

        return post_id
        








lm = LoginManager()
@lm.user_loader
def load_user():
    return "test"

app = Flask(__name__)

def create_app():
    app.secret_key = os.urandom(24)

    app.config["MYSQL_USER"] = 'b0dd62d51c1994'
    app.config["MYSQL_PASSWORD"] = '589ca3ad'
    app.config["MYSQL_HOST"] = 'eu-cdbr-west-03.cleardb.net'
    app.config["MYSQL_DB"] = 'heroku_1fed0ad0dd81591'
    app.config.from_object("settings")

    app.add_url_rule("/", view_func=load_user)
    app.add_url_rule("/posts/<int:post_key>", view_func=post_page)
    app.add_url_rule("/post", view_func=post_page)
    app.add_url_rule("/new_post", view_func=create_post_page, methods=["GET","POST"])
    app.add_url_rule("/register", view_func=register_page, methods=["GET","POST"])
    app.add_url_rule("/register_teachers", view_func=Tregister_page, methods=["GET","POST"])
    app.add_url_rule("/login", view_func=login_page, methods=["GET","POST"])
    app.add_url_rule("/about_us", view_func=about_page)
    app.add_url_rule("/test", view_func=read_page)
    app.add_url_rule("/logout", view_func=out_page)
    app.add_url_rule("/delete", view_func=delete_page)
    app.add_url_rule("/add_item", view_func=add_item, methods=["GET","POST"])
    app.add_url_rule("/new_password", view_func=change_password, methods=["GET","POST"])
    app.add_url_rule("/Update_post/<int:post_key>", view_func=update_post, methods=["GET","POST"])
    app.add_url_rule("/delete_post/<int:post_key>", view_func=post_delete_page, methods=["GET","POST"])

    
    return app

if __name__ == "__main__":
    app = create_app()
    lm.init_app(app)
    db = MySQL(app)
    app.config["db"] = db
    database = Database()
    app.run(host="0.0.0.0", port=8080, debug=True)

    












from datetime import datetime
from flask_mysqldb import MySQL
from flask import current_app, render_template,request,redirect,url_for, abort
from random import randint
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import LoginManager, login_user, current_user
from flask import Flask, session, redirect, url_for, escape, request

database = Database()

def home_page():
    data = database.get_posts()
    if 'username' in session:
        return render_template("home.html", posts = data, user_id = session['username'])
    else:
        return render_template("home.html", posts = data)

def post_page(post_key):
    data = database.get_post(post_key)
    print("******************")
    if 'username' in session:
        if int(session['user_type']):
                    
            db = current_app.config["db"]
            cur = db.connection.cursor()
            id = int(data[0][0])
            print(id)
            cur.execute((''' SELECT posts.Author_id FROM posts WHERE posts.Post_id= %s''' % (id)))  
            auth = cur.fetchall()
            if int(auth[0][0]) == int(session["user_id"]):
                return render_template("post.html", post=data, user_id = session["user_id"])
            else:
                return render_template("post.html", post=data)
    else:
        return render_template("post.html", post=data)


def add_item():
    if request.method == "GET":
        return render_template("Add_item.html")
    else:
        name = request.form["name"]
        amount = request.form["amount"]
        
        db = current_app.config["db"]
        cur = db.connection.cursor()
        print(name)
        cur.execute("SELECT inventory.Amount FROM inventory WHERE inventory.Item_name="+"'"+name+"'")
        data = cur.fetchall()
        print(data)
        if len(data) >= 1:
            n = int(data[0][0])
            n+= int(amount)
            print("*"*30)
            cur.execute(" UPDATE inventory SET inventory.Amount = %s WHERE inventory.Item_name= %s",(n,name))
            db.connection.commit()
        else:
            cur.execute("INSERT INTO inventory (Item_name, Amount) VALUES (%s, %s)",(name, int(amount)))
            db.connection.commit()
        
    
    return redirect(url_for("home_page"))




def about_page():
    if 'username' in session:
        return render_template("about.html", user_id = session["username"])
    else:
        return render_template("about.html")

def read_page():
    db = current_app.config["db"]
    cur = db.connection.cursor()
    cur.execute(''' SELECT posts.School_id, posts.Author_id, school_web.School_Web  FROM posts JOIN school_web WHERE school_web.School_id = 3''')
    data = cur.fetchall()
    return 'done!'

def create_post_page():
    if request.method == "GET":
        if 'username' in session:
            if 'user_type' in session:
                if int(session['user_type']):
                    return render_template("create_post.html")
                else:
                    return render_template("nopermission.html")
            else:
                return render_template("nopermission.html")
        else:
            return render_template("nopermission.html")
    else:
        form_title = request.form["title"]
        form_content = request.form["content"]
        form_school = request.form["school"]
        form_students = int(request.form["students"])
        needs = []
        for i in range(5):
            selected = request.form["row-"+str(i)+"-office"]
            if selected not in needs:
                if selected != "None":
                    needs.append(selected)
        print(needs)
        key = database.new_post(form_title, form_content, form_school, form_students, needs, int(session["user_id"]))
        if key==0:
            return render_template("create_post.html", error = "error")
        else:
            return redirect(url_for("post_page", post_key = key))

def update_post(post_key):
    if request.method == "GET":
        data = database.get_post(post_key)
        return render_template("update.html", post=data)
    else:
        form_title = request.form["title"]
        form_content = request.form["content"]
        
        db = current_app.config["db"]
        cur = db.connection.cursor()
        id = int(post_key)
        if len(form_title) > 3:
            cur.execute(''' UPDATE posts SET posts.Title ='''+"'"+form_title+"'"+ " WHERE posts.Post_id= %s"%(id))
        if len(form_content) > 3:
            cur.execute(''' UPDATE posts SET posts.Content='''+"'"+form_content+"'"+ " WHERE posts.Post_id= %s"%(id))
        db.connection.commit()
        return redirect(url_for("post_page", post_key = post_key))


def class_test_page():
    if request.method == "GET":
        return render_template("create_post.html")
    else:
        form_title = request.form["title"]
        form_content = request.form["content"]
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute("INSERT INTO posts (Title, Content, School_id, Author_id, StudentNumber) VALUES (%s, %s, %s, %s, %s)",(form_title, form_content, 2,3,40))
        db.connection.commit()
        return "added"

def check_reg(Email,Password,Name, Surname, City, Phone_number):
    errors= ["","","","","",""]
    a = 0
    if "@" not in Email:
        errors[0] = "Invalid Email"
        a=1
    if len(Password)<5:
        errors[1] = "Password is too short"
        a=1
    if len(Name)<4:
        errors[2] = "Name is too short"
        a=1
    if len(Surname)<4:
        errors[3] = "Surname is too short"
        a=1
    if len(Phone_number)!=11:
        errors[4] = "Invalid Phone Number"
        a=1
    return errors , a


def register_page():
    if request.method == "GET":
            return render_template("register.html")
    else:
        Email = request.form["email"]
        Password = request.form["password"]
        Name = request.form["name"]
        Surname = request.form["surname"]
        City = request.form["City"]
        Phone_number = request.form["Phone Number"]
        errors, a = check_reg(Email,Password,Name,Surname,City,Phone_number)
        if a:
            return render_template("register.html", errors = errors)
        hashed = hasher.hash(Password)
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute("INSERT INTO users (Email, User_type, Password, First_name, Last_name, Phone, City) VALUES (%s, %s, %s, %s, %s, %s, %s)",(Email, "User", hashed, Name, Surname, Phone_number, City ))
        db.connection.commit()
        return redirect(url_for("home_page"))

def Tregister_page():
    if request.method == "GET":
            return render_template("teacher_reg.html")
    else:
        Email = request.form["email"]
        Password = request.form["password"]
        Name = request.form["name"]
        Surname = request.form["surname"]
        City = request.form["City"]
        Phone_number = request.form["Phone Number"]
        Course = request.form["Course"]
        errors, a = check_reg(Email,Password,Name,Surname,City,Phone_number)
        if a:
            return render_template("register.html", errors = errors)
        hashed = hasher.hash(Password)
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute("INSERT INTO teacher (Email, Course, Password, First_name, Last_name, Phone, City) VALUES (%s, %s, %s, %s, %s, %s, %s)",(Email, Course, hashed, Name, Surname, Phone_number, City ))
        db.connection.commit()
        return redirect(url_for("home_page"))

def login_page():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user_type=0
        Email = request.form["email"]
        Password = request.form["password"]
        
        db = current_app.config["db"]
        cur = db.connection.cursor()
        cur.execute(''' SELECT users.Password, users.First_name ,users.User_id FROM users WHERE users.Email = '''+"'"+str(Email)+"'")
        data = cur.fetchall()
        if len(data)==0:
            cur.execute(''' SELECT teacher.Password, teacher.First_name, teacher.Teacher_id FROM teacher WHERE teacher.Email = '''+"'"+str(Email)+"'")
            data = cur.fetchall()
            if len(data)==0:
                return render_template("login.html", error = "error")
            else:
                user_type = 1
        print(data[0][0])
        if hasher.verify(Password, data[0][0]):
            session['user_type'] = str(user_type)
            session['username'] = str(data[0][1])
            session['user_id'] = str(data[0][2])
            test = session['username']
            return redirect(url_for("home_page"))
        else:
            return render_template("login.html", error = "error")
        print(Email)
        print(data)
        return render_template("login.html")

def out_page():
    session.pop('username', None)
    session.pop('user_type', None)
    session.pop('user_id', None)
    return redirect(url_for("home_page"))

def change_password():
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        Password = request.form["password"]
        if "user_id" in session:
            print("test")
            id = int(session["user_id"])
            user_type = int(session["user_type"])
            print("test")
            db = current_app.config["db"]
            cur = db.connection.cursor()
            hashed = hasher.hash(Password)
            if user_type:
                cur.execute(''' UPDATE teacher SET teacher.Password ='''+"'"+hashed+"'"+ " WHERE teacher.Teacher_id= %s"%(id))
            else:
                cur.execute(''' UPDATE users SET users.Password ='''+"'"+hashed+"'"+ " WHERE users.User_id= %s"%(id))
            db.connection.commit()    
        
            return redirect(url_for("home_page"))


def delete_page():
    db = current_app.config["db"]
    cur = db.connection.cursor()
    if 'user_type' in session:
        id = int(session["user_id"])
        if int(session['user_type']):
            cur.execute("DELETE FROM teacher WHERE teacher.Teacher_id= %s"%(id))
        else:
            cur.execute("DELETE FROM users WHERE users.User_id= %s"%(id))
        db.connection.commit() 
    session.pop('username', None)
    session.pop('user_type', None)
    session.pop('user_id', None)
    return redirect(url_for("home_page"))

def post_delete_page(post_key):

    db = current_app.config["db"]
    cur = db.connection.cursor()
    id = int(post_key)
    cur.execute("DELETE FROM posts WHERE posts.Post_id= %s"%(id))
    db.connection.commit()
    return redirect(url_for("home_page"))

