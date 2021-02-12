import sqlite3
from discord.ext.commands import Bot
from discord.ext import tasks
from .util.time_utils import current_hour

class KouluBot(Bot):
    def __init__(self, config: dict):
        self.config = config
        self.database = None
        self.db_table_titles = self.config['db_tables']
        super().__init__(command_prefix=self.config['commandPrefix'])
        self.init_database()
        self.init_commands()

    def init_database(self):
        try:
            self.database = sqlite3.connect(self.config['databasePath'])
            print(f'Database {self.config["databasePath"]} connected successfully')

            # make sure tables exists
            q = ('''CREATE TABLE IF NOT EXISTS courses (
                        id integer PRIMARY KEY AUTOINCREMENT,
                        peppi_id text,
                        title text,
                        channel_id integer
                        );
                ''',)
            self.database_query(q)

            q = ('''CREATE TABLE IF NOT EXISTS deadlines (
                        id integer PRIMARY KEY AUTOINCREMENT,
                        course_id integer,
                        timestamp text,
                        message text
                        );
                 ''',)
            self.database_query(q)
            
            q = ('''CREATE TABLE IF NOT EXISTS lectures (
                        id integer PRIMARY KEY AUTOINCREMENT,
                        course_id integer,
                        start_timestamp text,
                        end_timestamp text,
                        location text
                        );
                 ''',)
            self.database_query(q)

        except Exception as err:
            print(f'Error while creating database at {self.config["databasePath"]}')
            print(err)
            raise

    def init_commands(self):
        for ev in self.config['events']:
            try:
                self.load_extension(f'src.events.{ev}')
                print(f'Successfully loaded event: {ev}')

            except Exception as err:
                print(f'Failed to load event: {ev}')
                print(err)

    def database_query(self, query):
        cursor = self.database.cursor()
        cursor.execute(*query)
        self.database.commit()
        return cursor.lastrowid

    def database_return(self, query, fetch_all=False):
        cursor = self.database.cursor()
        cursor.execute(*query)
        return cursor.fetchall() if fetch_all else cursor.fetchone()
    
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        #self.alarms_checker.start()
        #print('Alarms checker started')

    @tasks.loop(minutes=15)
    async def alarm_checker(self):
        if current_hour() == 12:
            self.check_deadlines()
        self.check_lecture_times()

    def check_deadlines(self):
        # onko tälle päivälle deadlineja
        #   SELECT * FROM deadlines WHERE timestamppi on tälle päivälle
        # jos on ilmoita oikealla kanavalla
        # poista deadline db:stä
        pass

    def check_lecture_times(self):
        # Tarkista ajat onko 15 min sisällä alkamassa
        #   SELECT * FROM lectures WHERE timestamppi - nykyaika alle 15min
        # ilmoita kanavalle
        # poista merkintä lectures tablesta
        pass
