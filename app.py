from flask import Flask, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mashov import MashovAPI, LoginFailed
from iscool import Iscool
from extras import compare
from datetime import datetime


app = Flask(__name__)
"""
To limit the possibility of people stealing data. Again, this is not so secure.
USE THIS SCRIPT AT YOUR OWN RISK
(using it locally should be fine. Using the version on heroku (https://beitbiram.herokuapp.com/) isn't that secure. If you're running this locally feel free to remove the rate limiter)
"""
ratelimiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["50 per hour"]
) 

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Home page
    Gets nothing
    Returns the correct html file to present
    """
    if request.method == "GET": #  Checks if the method used it a GET method (when you login to the website)
        return render_template("home.html")
    username = request.form["username"] #  Gets the username you inserted
    password = request.form["password"] #  Gets the password you inserted
    mashov = MashovAPI(username=username, password=password, schoolID=340216, schoolName="בית בירם -  הריאלי - חיפה")
    del username #  Just in case
    del password
    try:
        mashov.login() #  Attempts to login to your Mashov account
    except LoginFailed:
        return "Login Failed. Try again."
    my_class = mashov.class_name #  Gets your class from your Mashov account
    iscool_class = ""
    if "יב" in my_class:
        iscool_class += "12"
        my_class = my_class.replace("יב", "")
    elif "יא" in my_class:
        iscool_class += "11"
        my_class = my_class.replace("יא", "")
    elif "י" in my_class:
        iscool_class += "10"
        my_class = my_class.replace("י", "")
    else:
        return "Not a valid class."
    if len(my_class) == 1:
        my_class = "0" + my_class
    iscool_class += my_class #  A variable that declares your class in a way Iscool understands
    week = []
    for i in range(6):
        today_mashov = mashov.get_day(i) #  Gets the day's timetable from your Mashov account
        iscool = Iscool(iscool_class)
        today_iscool = iscool.get_day(i) #  Gets the day's timetable from Iscool
        today = compare(today_iscool.lessons, today_mashov.lessons, iscool.times) #  Finds the correct timetable with changes and everything for you
        today = [lesson.to_dict() for lesson in today]
        week.append(today)
    week.append(week.pop(0))
    day = datetime.now().weekday()
    day += 1
    if day > 8:
        day -= 8
    return render_template("timetable.html", lessons=week[day], week=week)


@app.route("/api", methods=["POST"])
def api():
    """
    The API side of the website. No real need for it if I'm being honest
    I needed it for when the site was still on heroku but now it's not
    Feel free to delete it I guess

    It does the same as the main page so I don't see a reason to fully document this part. If you want to, be my guest
    """
    username = request.form["username"]
    password = request.form["password"]
    mashov = MashovAPI(username=username, password=password, schoolID=340216, schoolName="בית בירם -  הריאלי - חיפה")
    del username
    del password
    try:
        mashov.login()
    except LoginFailed:
        return "Login Failed. Try again."
    if not mashov.is_logged_in:
        return "Wrong username+password combination. Please try again."
    today_mashov = mashov.get_today()
    my_class = mashov.class_name
    iscool_class = ""
    if "יב" in my_class:
        iscool_class += "12"
        my_class.replace("יא", "")
    elif "יא" in my_class:
        iscool_class += "11"
        my_class.replace("יא", "")
    elif "י" in my_class:
        iscool_class += "10"
        my_class.replace("י", "")
    else:
        return "Not a valid class."
    if len(my_class) == 1:
        my_class = "0" + my_class
    iscool_class += my_class
    iscool = Iscool(iscool_class)
    today_iscool = iscool.get_today()
    today = compare(today_iscool.lessons, today_mashov.lessons, iscool.times)
    today = [lesson.to_dict() for lesson in today]
    lessons = {}
    for i in today:
        lessons[f"{i['number']}"] = i
    return lessons


if __name__ == "__main__":
    app.run()