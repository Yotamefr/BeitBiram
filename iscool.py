import requests
from bs4 import BeautifulSoup
from extras import Day, Lesson
from datetime import datetime


class Iscool:
    """
    A class that represents the IscoolAPI
    I made it alone
    """
    BASE_URL="http://beitbiram.iscool.co.il/default.aspx?view=8&cls={}&m=9&y=2020&sa=False"
    def __init__(self, my_class: str):
        """
        Parameters
        ------------
        my_class -> Represents the class name in which the user is in
        ------------
        """
        self.my_class = my_class
        self.response = requests.get(self.BASE_URL.format(my_class))
        bs = BeautifulSoup(self.response.text, features="lxml")
        cells = bs.find_all("td", {"class": "TTCell"}) #  Find all tables
        classes = [cell.div for cell in cells]
        while None in classes:
            classes.remove(None)
        if classes == []:
            classes = [cell.td for cell in cells]
            while None in classes:
                classes.remove(None)
        classes = [i.text for i in classes]
        tr = bs.find_all("tr", {
            "bgcolor":"#ffffff",
            "valign":"top"
        })
        for i in tr:
            while "\n" in i.contents:
                i.contents.remove("\n")
        self.days = []
        for j in range(7):
            day = []
            for i in tr:
                day.append(i.contents[j])
            self.days.append(day)

        self.times = self.days[0]
        del self.days[0]
    
    def get_lesson(self, day: int, lesson_number: int):
        """
        Parameters
        ------------
        day -> Represents the day number

        lesson_number -> Represents the lesson's number in the day
        ------------
        """
        if not isinstance(day, int): #  Honestly, I don't know why but for some reason `day` sometimes became something that isn't an integer, so I added this to fix it
            return
        lessons = []
        for i in range(0, len(self.days[day][lesson_number].contents)-1, 1):
            subject = None
            if not self.days[day][lesson_number].contents == ["\n"] and not self.days[day][lesson_number].contents == [] and not self.days[day][lesson_number].contents[i] == "\n":
                if not self.days[day][lesson_number].contents[i].text == "":
                    try:
                        self.days[day][lesson_number].contents[i].td.attrs["class"]
                        try:
                            """
                            Handling exams
                            """
                            classroom = self.days[day][lesson_number].contents[2].text.split(", ")[1]
                            subject = self.days[day][lesson_number].contents[2].text.split(", ")[0]
                            teacher =  self.days[day][lesson_number].contents[3].text.replace("לקבוצה של ", "")
                            teacher = teacher.split(" ")
                            teacher.reverse()
                            teacher = " ".join(teacher)
                        except:
                            """
                            Handling changes in the timetable
                            """
                            classroom = self.days[day][lesson_number].contents[1].contents[0].text.split(" -> ")[1].replace("חדר: ", "")
                            subject = ""
                            teacher =  self.days[day][lesson_number].contents[1].contents[0].text.split(" -> ")[0]
                            teacher = teacher.split(" ")
                            teacher = [teacher[2], teacher[0], teacher[1]] if len(teacher) == 3 else teacher.reverse()
                            teacher = " ".join(teacher)
                    except:
                        try:
                            """
                            Handling the timetable normally
                            """
                            teacher = self.days[day][lesson_number].contents[i].contents[len(self.days[day][lesson_number].contents[i].contents) - 1].split(" ")
                            classroom = self.days[day][lesson_number].contents[i].contents[1]
                        except:
                            try:
                                """
                                Handling exams
                                Yes. Again.
                                """
                                teacher = self.days[day][lesson_number].contents[i].contents[0].contents[0].contents[2].__str__()
                                teacher = teacher.replace("לקבוצה של ", "")
                                teacher = teacher.split(" ")
                                classroom = self.days[day][lesson_number].contents[i].contents[0].contents[0].contents[0].__str__().split(", ")[1]
                                subject = self.days[day][lesson_number].contents[i].contents[0].contents[0].contents[0].__str__().split(", ")[0]
                            except:
                                """
                                Handling changes in the timetable
                                Yes. Again.
                                """
                                classroom = self.days[day][lesson_number].contents[1].contents[0].text.split(" -> ")[1].replace("חדר: ", "")
                                subject = ""
                                teacher =  self.days[day][lesson_number].contents[1].contents[0].text.split(" -> ")[0]
                                teacher = teacher.split(" ")
                                teacher = [teacher[2], teacher[0], teacher[1]] if len(teacher) == 3 else teacher
                        teacher.reverse()
                        teacher = " ".join(teacher)
                        try:
                            classroom = classroom.replace("(", "")
                            classroom = classroom.replace(")", "")
                        except:
                            classroom = ""
                    lesson = Lesson(
                        lesson=self.days[day][lesson_number].contents[i].contents[0].text if subject is None else subject,
                        lesson_number=lesson_number, 
                        lesson_time=self.times[lesson_number].contents[0].contents[2].text,
                        teacher=teacher,
                        classroom=classroom
                    )
                    lessons.append(lesson)
        return lessons
    
    def get_day(self, day):
        """
        Parameters
        ------------
        day -> Represents the day number
        ------------
        """
        lessons = []
        for i in range(len(self.days[day])):
            lessons.append(self.get_lesson(day, i))
        while None in lessons:
            lessons.remove(None)
        return Day(day=day + 1, items=lessons)

    def get_today(self):
        """
        Parameters
        ------------
        ------------
        """
        today = datetime.now().weekday()
        today += 1
        if today == 7:
            today = 0
        return self.get_day(today)
