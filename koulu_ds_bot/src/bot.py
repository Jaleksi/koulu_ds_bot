import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from discord.ext.commands import Bot, CommandNotFound
from discord.ext import tasks
from discord import Embed
from .util.time_utils import current_hour, epoch_now, epoch_to_readable_time

class KouluBot(Bot):
    def __init__(self, config):
        self.config = config
        self.database = None
        self.logger = None
        self.last_deadlines_check = 0
        super().__init__(command_prefix=self.config['commandPrefix'])
        self.init_logging()
        self.init_database()
        self.init_commands()

    def init_logging(self):
        log_path = f'{self.config["logDirPath"]}/{epoch_now()}.log'

        handler = RotatingFileHandler(
            filename=log_path,
            mode='a+',
            maxBytes=4096,
            backupCount=2
        )

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='[%d.%m.%Y %H:%M:%S]',
            handlers = [
                handler,
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger('bot_logger')
        self.logger.info('Logging initiated')

    def init_database(self):
        try:
            self.database = sqlite3.connect(self.config['databasePath'])
            self.logger.info(f'Database {self.config["databasePath"]} connected successfully')

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

            # make sure tables exists
            for table_name, keys in tables.items():
                q = (f'CREATE TABLE IF NOT EXISTS {table_name} ({",".join(keys)})',)
                self.database_query(q)

        except Exception as err:
            self.logger.error(f'Error while creating database at {self.config["databasePath"]}')
            self.logger.error(err)
            raise

    def init_commands(self):
        for ev in self.config['events']:
            try:
                self.load_extension(f'src.events.{ev}')
                self.logger.info(f'Successfully loaded event: {ev}')

            except Exception as err:
                self.logger.warning(f'Failed to load event: {ev}')
                self.logger.warning(err)

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
        self.logger.info(f'Logged in as {self.user}')
        self.alarms_checker.start()
        self.logger.info('Alarms checker started')

    @tasks.loop(minutes=10)
    async def alarms_checker(self):
        # Check deadlines only once a day at 12 o'clock
        time_since_last_check = epoch_now() - self.last_deadlines_check
        twelve_hours = 43200
        if current_hour() == 12 and time_since_last_check > twelve_hours:
            self.last_deadlines_check = epoch_now()
            await self.check_deadlines()

        await self.check_lecture_times()

    async def check_deadlines(self):
        self.logger.debug('Checking deadlines')
        q = ('''SELECT
                    deadlines.id,
                    deadlines.message,
                    courses.channel_id
                FROM deadlines
                INNER JOIN courses ON
                    courses.id=deadlines.course_id
                WHERE timestamp < ?
             ''',
             (self.last_deadlines_check,))
        triggered_deadlines = self.database_return(q, fetch_all=True)

        if not triggered_deadlines:
            self.logger.debug('No deadlines triggered')
            return

        self.logger.debug(f'Triggered {len(triggered_deadlines)} deadlines')

        for triggered in triggered_deadlines:
            e = Embed(title='Deadlinemuistutus', description=triggered[1])
            self.database_query((f'DELETE FROM deadlines WHERE id={triggered[0]}',))
            await self.get_channel(triggered[2]).send(embed=e)

    async def check_lecture_times(self):
        self.logger.debug('Checking lecture times')
        fifteen_minutes = 900
        trigger_time = epoch_now() + fifteen_minutes

        q = ('''SELECT
                    lectures.id,
                    lectures.start_timestamp,
                    lectures.end_timestamp,
                    lectures.location,
                    followed_lecture_types.title,
                    courses.channel_id
                FROM lectures
                INNER JOIN followed_lecture_types ON
                    lectures.lecture_type=followed_lecture_types.lecture_type
                INNER JOIN courses ON
                    courses.id=followed_lecture_types.course_id
                WHERE lectures.start_timestamp < ?
             ''', (trigger_time,))
        triggered_lectures = self.database_return(q, fetch_all=True)

        if not triggered_lectures:
            self.logger.debug('No lecture times triggered')
            return

        self.logger.debug(f'Triggered {len(triggered_lectures)} lectures')

        for triggered in triggered_lectures:
            desc = f'Ajankohta {epoch_to_readable_time(triggered[1])} - {epoch_to_readable_time(triggered[2])}'
            desc += f'\nIlmoitettu sijainti: {triggered[3]}'
            e = Embed(title=triggered[4], description=desc)
            self.database_query((f'DELETE FROM lectures WHERE id={triggered[0]}',))
            await self.get_channel(triggered[5]).send(embed=e)
