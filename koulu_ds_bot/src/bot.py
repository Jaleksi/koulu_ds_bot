import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from discord.ext.commands import Bot, CommandNotFound
from discord.ext import tasks
from discord import Embed
from .db.manager import DatabaseManager
from .util.time_utils import current_hour, epoch_now, epoch_to_readable_time

class KouluBot(Bot):
    def __init__(self, config):
        self.config = config
        self.logger = None
        self.db = DatabaseManager(self.config['databasePath'])
        super().__init__(command_prefix=self.config['commandPrefix'])
        self.init_logging()
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

    def init_commands(self):
        for ev in self.config['events']:
            try:
                self.load_extension(f'src.events.{ev}')
                self.logger.info(f'Successfully loaded event: {ev}')

            except Exception as err:
                self.logger.warning(f'Failed to load event: {ev}')
                self.logger.warning(err)

    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user}')
        self.alarms_checker.start()
        self.logger.info('Alarms checker started')

    @tasks.loop(minutes=10)
    async def alarms_checker(self):
        # trigger events which have start time in less than 15 minutes
        fifteen_minutes = 900
        trigger_time = epoch_now() + fifteen_minutes

        await self.check_deadlines(trigger_time)
        await self.check_lecture_times(trigger_time)

    async def check_deadlines(self, trigger):
        self.logger.debug('Checking deadlines')
        triggered_deadlines = self.db.fetch_triggered_deadlines(trigger)

        if not triggered_deadlines:
            self.logger.debug('No deadlines triggered')
            return

        self.logger.debug(f'Triggered {len(triggered_deadlines)} deadlines')

        for triggered in triggered_deadlines:
            e = Embed(title='Deadlinemuistutus', description=triggered[1])
            self.db.delete_deadline_by_id(triggered[0])
            await self.get_channel(triggered[2]).send(embed=e)

    async def check_lecture_times(self, trigger):
        self.logger.debug('Checking lecture times')
        triggered_lectures = self.db.fetch_triggered_lectures(trigger)

        if not triggered_lectures:
            self.logger.debug('No lecture times triggered')
            return

        self.logger.debug(f'Triggered {len(triggered_lectures)} lectures')

        for triggered in triggered_lectures:
            desc = f'Ajankohta {epoch_to_readable_time(triggered[1])} - {epoch_to_readable_time(triggered[2])}'
            desc += f'\nIlmoitettu sijainti: {triggered[3]}'
            e = Embed(title=triggered[4], description=desc)
            self.db.delete_lecture_by_id(triggered[0])
            await self.get_channel(triggered[5]).send(embed=e)
