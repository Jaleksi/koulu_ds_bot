import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from discord.ext.commands import Bot, CommandNotFound
from discord.ext import tasks
from discord import Embed
from .util.time_utils import current_hour, epoch_now, epoch_to_readable_time

class KouluBot(Bot):
    def __init__(self, config: dict):
        self.config = config
        self.database = None
        self.logger = None
        self.last_deadlines_check = 0
        super().__init__(command_prefix=self.config['commandPrefix'])
        self.init_logging()
        self.init_database()
        self.init_commands()

    def init_logging(self):
        start_time = epoch_now()
        log_path = f'{self.config["logDirPath"]}/{start_time}.log'

        handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=4096
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
        self.logger.info(f'Started logging at epoch {epoch_to_readable_time(start_time)}')

    def init_database(self):
        try:
            self.database = sqlite3.connect(self.config['databasePath'])
            self.logger.info(f'Database {self.config["databasePath"]} connected successfully')

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
                        location text,
                        lecture_type text
                        );
                 ''',)
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
        await self.check_deadlines()
        await self.check_lecture_times()

    async def check_deadlines(self):
        time_since_last_check = epoch_now() - self.last_deadlines_check
        twelve_hours = 43200

        if current_hour() != 12 or time_since_last_check < twelve_hours:
            return

        self.logger.debug('Checking deadlines')
        self.last_deadlines_check = epoch_now()
        q = (f'SELECT * FROM deadlines WHERE timestamp < {self.last_deadlines_check}',)
        triggered_deadlines = self.database_return(q, fetch_all=True)

        if not triggered_deadlines:
            self.logger.debug('No deadlines triggered')
            return

        self.logger.debug(f'Triggered {len(triggered_deadlines)} deadlines')

        for triggered in triggered_deadlines:
            channel_id = self.database_return((f'SELECT channel_id FROM courses WHERE id={triggered[1]}',))[0]
            e = Embed(title='Deadlinemuistutus', description=f'Tänään on viimeinen päivä hoitaa {triggered[3]}')
            self.database_query((f'DELETE FROM deadlines WHERE id={triggered[0]}',))
            await self.get_channel(channel_id).send(embed=e)

    async def check_lecture_times(self):
        self.logger.debug('Checking lecture times')
        fifteen_minutes = 900
        trigger_time = epoch_now() + fifteen_minutes

        q = (f'SELECT * FROM lectures WHERE start_timestamp < {trigger_time}',)
        triggered_lectures = self.database_return(q, fetch_all=True)

        if not triggered_lectures:
            self.logger.debug('No lecture times triggered')
            return

        self.logger.debug(f'Triggered {len(triggered_lectures)} lectures')

        for triggered in triggered_lectures:
            channel_id = self.database_return((f'SELECT channel_id FROM courses WHERE id={triggered[1]}',))[0]
            desc = f'Ajankohta {epoch_to_readable_time(triggered[2])} - {epoch_to_readable_time(triggered[3])}'
            desc += f'\nIlmoitettu sijainti: {triggered[4]}'
            desc += f'\nLuentotyyppi: {triggered[5]}'
            e = Embed(title='Luentomuistutus', description=desc)
            self.database_query((f'DELETE FROM lectures WHERE id={triggered[0]}',))
            await self.get_channel(channel_id).send(embed=e)
