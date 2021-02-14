import sqlite3
import logging
from discord.ext.commands import Bot
from discord.ext import tasks
from discord import Embed
from .util.time_utils import current_hour, epoch_now, epoch_to_readable_time

class KouluBot(Bot):
    def __init__(self, config: dict):
        self.config = config
        self.database = None
        self.db_table_titles = self.config['db_tables']
        super().__init__(command_prefix=self.config['commandPrefix'])
        self.init_logging()
        self.init_database()
        self.init_commands()

    def init_logging(self):
        start_time = epoch_now()
        logging.basicConfig(
            filename=f'{self.config["logDirPath"]}/{start_time}.log',
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='[%d.%m.%Y %H:%M:%S]'
        )
        logging.info(f'Started logging at epoch {epoch_to_readable_time(start_time)}')

    def init_database(self):
        try:
            self.database = sqlite3.connect(self.config['databasePath'])
            logging.info(f'Database {self.config["databasePath"]} connected successfully')

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
            logging.error(f'Error while creating database at {self.config["databasePath"]}')
            logging.error(err)
            raise

    def init_commands(self):
        for ev in self.config['events']:
            try:
                self.load_extension(f'src.events.{ev}')
                logging.info(f'Successfully loaded event: {ev}')

            except Exception as err:
                logging.warning(f'Failed to load event: {ev}')
                logging.warning(err)

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
        logging.info(f'Logged in as {self.user}')
        self.alarms_checker.start()
        logging.info('Alarms checker started')

    @tasks.loop(seconds=10)
    async def alarms_checker(self):
        if int(current_hour()) + 2 == 12: # returns gmt-time, FIN time is +2
            await self.check_deadlines()
        await self.check_lecture_times()

    async def check_deadlines(self):
        logging.debug('Checking deadlines')
        now = epoch_now()
        q = (f'SELECT * FROM deadlines WHERE timestamp < {now}',)
        triggered_deadlines = self.database_return(q, fetch_all=True)

        if not triggered_deadlines:
            logging.debug('No deadlines triggered')
            return
        
        logging.debug(f'Triggered {len(triggered_deadlines)} deadlines')

        for triggered in triggered_deadlines:
            channel_id = self.database_return((f'SELECT channel_id FROM courses WHERE id={triggered[1]}',))[0]
            e = Embed(title="Deadlinemuistutus", description=f'Tänään on viimeinen päivä hoitaa {triggered[3]}')
            self.database_query((f'DELETE FROM deadlines WHERE id={triggered[0]}',))
            await self.get_channel(channel_id).send(embed=e)

    async def check_lecture_times(self):
        logging.debug('Checking lecture times')
        fifteen_minutes = 900
        trigger_time = epoch_now() + fifteen_minutes

        q = (f'SELECT * FROM lectures WHERE start_timestamp < {trigger_time}',)
        triggered_lectures = self.database_return(q, fetch_all=True)

        if not triggered_lectures:
            logging.debug('No lecture times triggered')
            return
        
        logging.debug(f'Triggered {len(triggered_lectures)} lectures')

        for triggered in triggered_lectures:
            channel_id = self.database_return((f'SELECT channel_id FROM courses WHERE id={triggered[1]}',))[0]
            desc = f'Luento {epoch_to_readable_time(triggered[2])} - {epoch_to_readable_time(triggered[3])}'
            desc += f'\nLuennon sijainniksi on ilmoitettu: {triggered[4]}'
            e = Embed(title="Luentomuistutus", description=desc)
            self.database_query((f'DELETE FROM lectures WHERE id={triggered[0]}',))
            await self.get_channel(channel_id).send(embed=e)
