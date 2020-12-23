import requests
from datetime import datetime
import json
from extras import Day, Lesson


class PasswordError(Exception):
    pass


class LoginFailed(Exception):
    pass


class MashovAPI:
    """
    MashovAPI
    Originally made by Xiddoc. Project can be found here: https://github.com/Xiddoc/MashovAPI
    Modifications were made by me, Yotamefr.
    """
    def __init__(self, username, **kwargs):
        """
        Parameters
        ------------
        username -> Represents the username
        ------------


        There are some weird stuff here. I might clean it in a while
        Again, this code wasn't made by me, just modified by me
        """
        self.url = "https://web.mashov.info/api/{}/"
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json, text/plain, */*',
                                     'Referer': 'https://web.mashov.info/students/login',
                                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
                                     'Content-Type': 'application/json'})
        self.username = username
        self.auth_ID = 0
        self.user_ID = self.auth_ID
        self.uid = self.auth_ID
        self.uID = self.auth_ID
        self.guid = self.auth_ID
        self.guID = self.auth_ID
        self.school_site = ""
        self.moodle_site = ""
        self.school_name = ""
        self.last_name = ""
        self.first_name = ""
        self.class_name = ""
        self.last_pass = ""
        self.last_login = ""
        self.school_years = []
        self.csrf_token = ""
        self.user_children = {}
        # Kwargs password
        if "password" in kwargs:
            self.password = kwargs["password"]
        else:
            self.password = False
        # Kwargs schoolData
        if "schoolData" in kwargs:
            self.school_data = kwargs["schoolData"]
        else:
            self.school_data = False
        # Kwargs schoolID
        if "schoolID" in kwargs:
            self.school_ID = kwargs["schoolID"]
        elif not self.school_data:
            self.school_data = self.get_schools()
            self.school_ID = self.get_school_ID_by_name(kwargs["schoolName"])
        self.current_year = datetime.now().year + 1

    def login(self):
        """
        Parameters
        ------------
        ------------
        """
        if not self.password:
            raise PasswordError("No password entered.")
        self.login_data = {'semel': self.school_ID,
                          'username': self.username,
                          'password': self.password,
                          'year': self.current_year}
        self.ret_data = self.send("login", "post", self.login_data)
        self.ret_text = json.loads(self.ret_data.text)
        if not self.ret_data.status_code == 200:
            self.is_logged_in = False
            raise LoginFailed()
        self.is_logged_in = True
        self.auth_ID = self.ret_text["credential"]["userId"]
        self.user_ID = self.auth_ID
        self.uid = self.auth_ID
        self.uID = self.auth_ID
        self.guid = self.auth_ID
        self.guID = self.auth_ID
        self.school_site = self.ret_text["accessToken"]["schoolOptions"]["schoolSite"]
        self.moodle_site = self.ret_text["accessToken"]["schoolOptions"]["moodleSite"]
        self.school_name = self.ret_text["accessToken"]["schoolOptions"]["schoolName"]
        self.last_name = self.ret_text["accessToken"]["children"][0]["familyName"]
        self.first_name = self.ret_text["accessToken"]["children"][0]["privateName"]
        self.class_name = f'{self.ret_text["accessToken"]["children"][0]["classNum"]}{self.ret_text["accessToken"]["children"][0]["classCode"]}'
        self.last_pass = self.ret_text["accessToken"]["lastPassSet"]
        self.last_login = self.ret_text["accessToken"]["lastLogin"]
        self.school_years = self.ret_text["accessToken"]["userSchoolYears"]
        self.csrf_token = self.ret_data.cookies["Csrf-Token"]
        self.session.headers.update({"x-csrf-token": self.csrf_token})
        self.user_children = self.ret_text["accessToken"]["children"]
        del self.username
        del self.password

    @property
    def timetable(self):
        return self.form_return(self.send(f"students/{self.user_ID}/timetable", "get"))

    def update_school_data(self):
        """
        Parameters
        ------------
        ------------
        """
        self.school_data = self.form_return(self.send("schools", "get"))

    def get_schools(self):
        """
        Parameters
        ------------
        ------------
        """
        self.update_school_data()
        return self.school_data()

    def get_school_ID_by_name(self, school):
        """
        Parameters
        ------------
        school -> Represents the school name
        ------------
        """
        if self.school_data:
            schoolData = self.school_data
        else:
            schoolData = self.update_school_data()
        for schools in schoolData:
            if schools["name"].find(school) == 0:
                return schools["semel"]

    def clear_session(self):
        """
        Parameters
        ------------
        ------------
        """
        return self.form_return(self.send("clearSession", "get"))

    def get_special_lessons(self):
        """
        Parameters
        ------------
        ------------
        """
        return self.get_private_lessons()

    def get_private_lessons(self):
        """
        Parameters
        ------------
        ------------
        """
        return self.form_return(self.send("students/{}/specialHoursLessons".format(self.auth_ID), "get"))

    def get_private_lesson_types(self):
        """
        Parameters
        ------------
        ------------
        """
        return self.form_return(self.send("lessonsTypes", "get"))

    @property
    def classes(self):
        return self.groups

    @property
    def groups(self):
        return self.form_return(self.send("students/{}/groups".format(self.auth_ID), "get"))

    @property
    def teachers(self):
        recipents = self.recipents
        teachers = []
        for i in recipents:
            if "הורים/" not in i["displayName"]:
                teachers.append(i)
        return teachers

    @property
    def recipents(self):
        return self.form_return(self.send("mail/recipients", "get"))

    def form_return(self, response):
        """
        Parameters
        ------------
        response -> Represents the response from the website
        ------------
        """
        if response.status_code != 200:
            return False
        else:
            try:
                return json.loads(response.text)
            except:
                return response.text

    def send(self, url, method="get", params={}, files={}):
        """
        Parameters
        ------------
        url -> Represents the url to go to

        method -> Represents the method to use. Can be either `get` or `post`

        params -> Represents the parameters to send to the website. Only use it on `post`

        files -> Pretty much the same as for the params
        ------------
        """
        return getattr(self.session, str(method).strip().lower())(self.url.format(url), data=json.dumps(params),
                                                                  files=files)

    def __str__(self):
        return json.dumps({
            "MashovAPI": {
                "url": self.url,
                "sessionH": dict(self.session.headers),
                "sessionC": self.session.cookies.get_dict(),
                "username": self.username,
                "password": self.password,
                "schoolData": self.school_data,
                "schoolID": self.school_ID,
                "currentYear": self.current_year,
                "loginData": self.login_data,
                "isLoggedIn": self.is_logged_in,
                "authID": self.auth_ID,
                "userID": self.user_ID,
                "uid": self.uid,
                "uID": self.uID,
                "guid": self.guid,
                "guID": self.guID,
                "schoolSite": self.school_site,
                "moodleSite": self.moodle_site,
                "schoolName": self.school_name,
                "lastName": self.last_name,
                "firstName": self.first_name,
                "className": self.class_name,
                "lastPass": self.last_pass,
                "lastLogin": self.last_login,
                "schoolYears": self.school_years,
                "csrfToken": self.csrf_token,
                "userChildren": self.user_children
            }})
    
    def get_day(self, day_num: int):
        """
        Parameters
        ------------
        day -> Represents the day number
        ------------
        """
        day = []
        timetable = []
        for i in self.timetable:
            if i["timeTable"]["day"] == day_num:
                timetable.append(i)
        for i in range(len(timetable)):
            for j in range(i+1, len(timetable), 1):
                if timetable[i]["timeTable"]["lesson"] > timetable[j]["timeTable"]["lesson"]:
                    temp = timetable[i]
                    timetable[i] = timetable[j]
                    timetable[j] = temp
        for i in timetable:
            if not "קפ'" in i["groupDetails"]["subjectName"]: #  We don't need that. It's useless.
                if len(day) > 0:
                    while i["timeTable"]["lesson"] > day[-1].number + 1:
                        day.append(Lesson(
                                            lesson="",
                                            lesson_number=day[-1].number + 1,
                                            lesson_time="",
                                            classroom="",
                                            teacher="",
                                        )
                                )
                i["groupDetails"]["groupTeachers"][0]["teacherName"] = i["groupDetails"]["groupTeachers"][0]["teacherName"].replace("-", " ")
                day.append(Lesson(
                                    lesson=i["groupDetails"]["subjectName"], 
                                    lesson_number=i["timeTable"]["lesson"], 
                                    lesson_time="", 
                                    classroom=i["timeTable"]["roomNum"], 
                                    teacher=i["groupDetails"]["groupTeachers"][0]["teacherName"]
                                 )
                           )
        return Day(day_num, day)
    
    def get_today(self):
        """
        Parameters
        ------------
        ------------
        """
        today = datetime.now().weekday()
        today += 2
        if today > 7:
            today -= 7
        return self.get_day(today)
