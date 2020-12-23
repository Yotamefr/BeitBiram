class Lesson:
    """
    This class resembles each Lesson. I made it just so it would be easier to code it then use dictionaries
    """
    def __init__(self, lesson: str, lesson_number: str, lesson_time: str, teacher: str, classroom: str):
        """
        Parameters
        ------------
        lesson -> Represents the lesson subject

        lesson_number -> Represents the lesson number

        lesson_time -> Represents the lesson time

        teacher -> Represents the teacher

        classroom -> Represents teh classroom in which the lesson will be in
        ------------

        All parameters can be None
        """
        self.lesson = lesson
        self.number = lesson_number
        self.time = lesson_time
        self.teacher = teacher
        self.classroom = classroom

    def to_dict(self):
        return {
            "lesson": self.lesson,
            "number": self.number,
            "time": self.time,
            "teacher": self.teacher,
            "classroom": self.classroom
        }

    def __str__(self):
        return f"שיעור: {self.lesson}.\tשיעור מספר: {self.number}.\tזמן: {self.time}.\tמורה: {self.teacher}.\tכיתה: {self.classroom}"
    

class Day:
    """
    This class represents a Day in the week. Was easier for me to use a class instead of a dictionary
    """
    def __init__(self, day: int, items: list):
        """
        Parameters
        ------------
        day -> Represents the day number

        items -> Represents the lessons in the day
        ------------
        """
        days = {
            "0": "ראשון",
            "1": "שני",
            "2": "שלישי",
            "3": "רביעי",
            "4": "חמישי",
            "5": "שישי",
        }
        while day > 5:
            day -= 5
        while day < 0:
            day += 5
        self.day = days[f"{day}"]
        self.lessons = items
    
    def __str__(self):
        lessons = ""
        for i in self.lessons:
            lessons += f"{i}\n"
        lessons = lessons[:-1]
        return f"יום: {self.day}.\n\n\nשיעורים: {lessons}"


def find_lesson(iscool_lessons: list, teacher_name: str):
    """
    Parameters
    ------------
    iscool_lessons -> Represents the iscool lessons

    teacher_name -> Represents the teacher name
    ------------
    """
    for i in range(len(iscool_lessons)):
        if iscool_lessons[i].teacher == teacher_name:
            return iscool_lessons[i]


def compare(iscool_lessons: list, mashov_lessons: list, times: list):
    """
    Parameters
    ------------
    iscool_lessons -> Represents the iscool lessons

    mashov_lessons -> Represents the mashov lessons

    times -> Represents the list of `times` in the timetable
    ------------
    """
    classes = []
    for i in range(len(mashov_lessons)):
        if mashov_lessons[0].number == 1:
            lesson = find_lesson(iscool_lessons[i + 1], mashov_lessons[i].teacher)
        else:
            lesson = find_lesson(iscool_lessons[i], mashov_lessons[i].teacher)
        if isinstance(lesson, Lesson):
            classes.append(lesson)
        else:
            mashov_lessons[i].time = times[len(classes) + 1].contents[0].contents[2].text
            classes.append(mashov_lessons[i])
    return classes
