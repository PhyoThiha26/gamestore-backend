from flask import Blueprint,render_template,request,redirect,session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

from app.models import User

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")
    
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id

            session["username"] = user.username

            session["role"] = user.role

            return redirect("/admin/dashboard")

        flash("Invalid username or password")

        return redirect("/login")
    
    return render_template("login.html")


@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/login")