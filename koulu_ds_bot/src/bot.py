import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from discord.ext.commands import Bot, CommandNotFound
from discord.ext import tasks
from discord import Embed
from .db.manager import DatabaseManager
from .events.update_lecture_times import get_updated_lectures
from .util.time_utils import current_hour, epoch_now, epoch_to_readable_time


class KouluBot(Bot):
    def __init__(self, config: dict) -> None:
        self.config = config
        self.db = DatabaseManager(self.config['databasePath'])
        self.last_deadlines_check = 0
        super().__init__(command_prefix=self.config['commandPrefix'])
        self.logger = self.init_logging()
        self.init_commands()

    def init_logging(self) -> logging.Logger:
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

        logger = logging.getLogger('bot_logger')
        logger.info('Logging initiated')
        return logger

    def init_commands(self) -> None:
        for ev in self.config['events']:
            try:
                self.load_extension(f'src.events.{ev}')
                self.logger.info(f'Successfully loaded event: {ev}')

            except Exception as err:
                self.logger.warning(f'Failed to load event: {ev}')
                self.logger.warning(err)

    async def on_ready(self) -> None:
        self.logger.info(f'Logged in as {self.user}')
        self.alarms_checker.start()
        self.logger.info('Alarms checker started')

    @tasks.loop(minutes=10)
    async def alarms_checker(self) -> None:
        # Check deadlines only once a day at 12 o'clock
        time_since_last_check = epoch_now() - self.last_deadlines_check
        twelve_hours = 43200
        if current_hour() == 12 and time_since_last_check > twelve_hours:
            self.last_deadlines_check = epoch_now()
            await self.check_deadlines()
            await self.update_lectures()

        await self.check_lecture_times()

    async def check_deadlines(self) -> None:
        self.logger.debug('Checking deadlines')
        triggered_deadlines = self.db.fetch_triggered_deadlines(self.last_deadlines_check)

        if not triggered_deadlines:
            self.logger.debug('No deadlines triggered')
            return

        self.logger.debug(f'Triggered {len(triggered_deadlines)} deadlines')

        for triggered in triggered_deadlines:
            e = Embed(title='Deadlinemuistutus', description=triggered[1])
            self.db.delete_deadline_by_id(triggered[0])
            await self.get_channel(triggered[2]).send(embed=e)

    async def check_lecture_times(self) -> None:
        self.logger.debug('Checking lecture times')
        fifteen_minutes = 900
        trigger_time = epoch_now() + fifteen_minutes
        triggered_lectures = self.db.fetch_triggered_lectures(trigger_time)

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

    async def update_lectures(self) -> None:
        self.logger.debug('Updating lectures')
        all_courses = self.db.get_all_courses()

        for course in all_courses:
            # get courses latest lecture times
            # course[1] = peppi_id
            new_lecture_times = get_updated_lectures(course[1])

            # if data wasn't found continue
            if new_lecture_times is None:
                continue

            # remove old lecture times
            self.db.delete_lectures_by_course_id(course[0])

            # add updated lectures to db
            for lecture in new_lecture_times:
                self.db.insert_new_lecture(course[0], lecture)
