from typing import List, Union
import sqlite3
from .util import fetch_to_dict

class DatabaseManager:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = fetch_to_dict
        self.cursor = self.connection.cursor()
        tables = {
            'courses': [
                'id integer PRIMARY KEY AUTOINCREMENT',
                'peppi_id text',
                'title text',
                'channel_id integer'
            ],
            'deadlines': [
                'id integer PRIMARY KEY AUTOINCREMENT',
                'course_id integer',
                'timestamp integer',
                'message text'
            ],
            'lectures': [
                'id integer PRIMARY KEY AUTOINCREMENT',
                'course_id integer',
                'start_timestamp integer',
                'end_timestamp integer',
                'location text',
                'lecture_type text'
            ],
            'followed_lecture_types': [
                'id integer PRIMARY KEY AUTOINCREMENT',
                'lecture_type text',
                'course_id integer',
                'title text'
            ]
        }

        for table_name, keys in tables.items():
            q = (f'CREATE TABLE IF NOT EXISTS {table_name} ({",".join(keys)})',)
            self.query(q)


    def query(self, q: tuple) -> int:
        '''
            q (tuple): (query (str), query parameters (tuple)) or
                       (query (str),)

            Execute given query and parameters (optional)
            return last modified item id
        '''
        self.cursor.execute(*q)
        self.connection.commit()
        return self.cursor.lastrowid

    def fetch(self, q: tuple, fetch_all: bool = False) -> Union[List, dict]:
        self.cursor.execute(*q)
        return self.cursor.fetchall() if fetch_all else self.cursor.fetchone()

    def fetch_triggered_deadlines(self, trigger_time: str) -> List:
        q = ('''SELECT
                    deadlines.id,
                    deadlines.message,
                    courses.channel_id
                FROM
                    deadlines
                INNER JOIN courses ON
                    courses.id=deadlines.course_id
                WHERE timestamp < ?
            ''',
            (trigger_time,))
        return self.fetch(q, fetch_all=True)

    def fetch_triggered_lectures(self, trigger_time: str) -> List:
        q = ('''SELECT
                    lectures.id,
                    lectures.start_timestamp,
                    lectures.end_timestamp,
                    lectures.location,
                    followed_lecture_types.title,
                    courses.channel_id
                FROM
                    lectures
                INNER JOIN followed_lecture_types ON
                    followed_lecture_types.lecture_type=lectures.lecture_type AND
                    followed_lecture_types.course_id=lectures.course_id
                INNER JOIN courses ON
                    courses.id=followed_lecture_types.course_id
                WHERE lectures.start_timestamp < ?
             ''', (trigger_time,))
        return self.fetch(q, fetch_all=True)

    def delete_lecture_by_id(self, lecture_id: str) -> None:
        self.query(('DELETE FROM lectures WHERE id=?', (lecture_id,)))

    def delete_lectures_by_course_id(self, course_id: str) -> None:
        self.query(('DELETE FROM lectures WHERE course_id=?', (course_id,)))

    def delete_deadline_by_id(self, deadline_id: str) -> None:
        self.query(('DELETE FROM deadlines WHERE id=?', (deadline_id,)))

    def delete_course_by_peppi_id(self, peppi_id: str) -> None:
        '''
            Delete course and all deadlines/lectures connected to it
        '''
        course_id = self.get_course_by_peppi_id(peppi_id)['id']
        for table in ['deadlines', 'lectures', 'followed_lecture_types']:
            self.query((f'DELETE FROM {table} WHERE course_id=?', (course_id,)))
        self.query(('DELETE FROM courses WHERE peppi_id=?', (peppi_id,)))

    def delete_followed_lecture(self, lecture_id: str) -> None:
        q = ('DELETE FROM followed_lecture_types WHERE id=?', (lecture_id,))
        self.query(q)

    def get_course_by_channel_id(self, channel_id: str) -> dict:
        q = ('SELECT * FROM courses WHERE channel_id=?', (channel_id,))
        return self.fetch(q)

    def get_course_by_peppi_id(self, peppi_id: str) -> dict:
        q = ('SELECT * FROM courses WHERE peppi_id=?', (peppi_id,))
        return self.fetch(q)

    def get_course_lectures(self, course_id: str) -> dict:
        q = ('''SELECT
                    *
                FROM
                    lectures
                WHERE
                    course_id=?
                ORDER BY
                    start_timestamp
            ''', (course_id,))
        return self.fetch(q, fetch_all=True)

    def get_course_lectures_by_type(self, course_id: str, lecture_type: str) -> List:
        q = ('''SELECT
                    id
                FROM
                    lectures
                WHERE
                    lecture_type=? AND
                    course_id=?
             ''', (lecture_type, course_id))
        return self.fetch(q, fetch_all=True)

    def get_course_followed_lecture_by_type(self, course_id: str, lecture_type: str) -> dict:
        q = ('''SELECT
                    *
                FROM
                    followed_lecture_types
                WHERE
                    lecture_type=? AND
                    course_id=?
            ''', (lecture_type, course_id))
        return self.fetch(q, fetch_all=False)

    def get_course_followed_lectures(self, course_id: str) -> List:
        q = ('''SELECT
                    *
                FROM
                    followed_lecture_types
                WHERE course_id=?
            ''', (course_id,))
        return self.fetch(q, fetch_all=True)

    def get_course_deadlines(self, course_id: str) -> List:
        q = ('''SELECT
                    courses.title,
                    deadlines.timestamp,
                    deadlines.message
                FROM
                    deadlines
                INNER JOIN
                    courses ON
                    deadlines.course_id=courses.id
                WHERE
                    courses.id=?
                ORDER BY
                    deadlines.timestamp
             ''', (course_id,))
        return self.fetch(q, fetch_all=True)

    def insert_new_followed_course(self,
                                   course_id: str,
                                   lecture_type: str,
                                   title: str
                                   ) -> None:
        q = ('''INSERT INTO
                    followed_lecture_types(lecture_type, course_id, title)
                VALUES(?, ?, ?)
            ''', (lecture_type, course_id, title))
        self.query(q)

    def insert_new_deadline(self,
                            course_id: str,
                            timestamp: str,
                            msg: str
                            ) -> None:
        q = ('''INSERT INTO
                    deadlines(course_id, timestamp, message)
                VALUES(?, ?, ?)
            ''', (course_id, timestamp, msg))
        self.query(q)

    def insert_new_course(self,
                          peppi_id: str,
                          title: str,
                          channel_id: str,
                          lectures: List[dict]
                          ) -> None:
        '''
            peppi_id (str): course's peppi id
            title (str): title for course
            channel_id (str): to which channel is course tied to
            lectures (list of dicts): list of lecture infos
        '''
        q = ('''INSERT INTO
                    courses(peppi_id, title, channel_id)
                VALUES(?, ?, ?)
             ''', (peppi_id, title, channel_id))
        entry_id = self.query(q)

        for lecture in lectures:
            self.insert_new_lecture(entry_id, lecture)

    def insert_new_lecture(self, course_id: int, lecture: dict) -> None:
        '''
            course_id (int): id for lecture's course
            lecture (dict): lecture info (parsed in uusikurssi.py)
        '''
        q = ('''INSERT INTO
                    lectures(course_id,
                             start_timestamp,
                             end_timestamp,
                             location,
                             lecture_type)
                VALUES(?, ?, ?, ?, ?)
            ''', (course_id, lecture['start'], lecture['end'], lecture['loc'], lecture['type']))
        self.query(q)

    def get_all_courses(self) -> List:
        return self.fetch(('SELECT * FROM courses',), fetch_all=True)

    def get_all_deadlines(self) -> List:
        q = ('''SELECT
                    courses.title,
                    deadlines.timestamp,
                    deadlines.message
                FROM
                    deadlines
                INNER JOIN
                    courses ON
                    deadlines.course_id=courses.id
                ORDER BY
                    timestamp
             ''',)
        return self.fetch(q, fetch_all=True)
