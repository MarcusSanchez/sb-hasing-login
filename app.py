from flask import Flask, redirect, session, render_template
from auth.forms import LoginForm, RegisterForm, FeedbackForm
from models import connect_db, db, Users, Feedback

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@localhost:5432/flask_auth"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "oh-so-secret"

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def render_homepage():
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_user():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template("register.j2", form=form)

    username = form.username.data
    email = form.email.data
    password = form.password.data
    first_name = form.first_name.data
    last_name = form.last_name.data

    user = Users.register(username, email, password, first_name, last_name)
    session["username"] = user.username

    db.session.commit()


@app.route("/login", methods=["GET", "POST"])
def signin_user():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("login.j2", form=form)

    username = form.username.data
    password = form.password.data

    user = Users.authenticate(username, password)
    if not user:
        form.username.errors = ["Invalid username/password."]
        return render_template("login.j2", form=form)

    session["username"] = user.username
    return redirect(f"/users/{user.username}")


@app.route("/logout")
def signout_user():
    session.pop("username")
    return redirect("/login")


@app.route("/users/<username>")
def render_user(username):
    if username != session.get("username", ""):
        return redirect("/login")

    user = Users.query.get(username)
    return render_template("show.j2", user=user)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    if username != session.get("username"):
        return redirect("/login")

    user = Users.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")


@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def render_feedback(username):
    if username != session.get("username", ""):
        return redirect("/login")

    form = FeedbackForm()
    if not form.validate_on_submit():
        return render_template("feedback.j2", form=form)

    title = form.title.data
    content = form.content.data

    feedback = Feedback(title=title, content=content, username=username)
    db.session.add(feedback)
    db.session.commit()

    return redirect(f"/users/{feedback.username}")


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username != session.get("username", ""):
        return redirect("/login")

    form = FeedbackForm(obj=feedback)
    if not form.validate_on_submit():
        return render_template("edit_feedback.j2", form=form, feedback=feedback)

    feedback.title = form.title.data
    feedback.content = form.content.data
    db.session.commit()

    return redirect(f"/users/{feedback.username}")


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if feedback.username != session.get("username", ""):
        return redirect("/login")

    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")
