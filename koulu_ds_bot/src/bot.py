from discord.ext.commands import Bot
import sqlite3

class KouluBot(Bot):
    def __init__(self, config: dict):
        self.config = config
        self.database = None
        super().__init__(command_prefix=self.config['commandPrefix'])
        self.init_database()
        self.init_commands()

    def init_database(self):
        try:
            self.database = sqlite3.connect(self.config['databasePath'])
            # make sure table exists
            q = 'CREATE TABLE IF NOT EXISTS kurssit (id text PRIMARY KEY, title text);'
            self.database_query(q)
            print(f'Database {self.config["databasePath"]} connected successfully')
        except Exception as err:
            print(f'Failed to connect database at {self.config["databasePath"]}')
            print(err)

    def init_commands(self):
        for ev in self.config['events']:
            try:
                self.load_extension(f'src.events.{ev}')
                print(f'Successfully loaded event: {ev}')

            except Exception as err:
                print(f'Failed to load event: {ev}')
                print(err)

    def database_query(self, query):
        try:
            cursor = self.database.cursor()
            cursor.execute(query)
            self.database.commit()

        except Exception as err:
            print(err)

    def database_return(self, query, fetch_all=False):
        try:
            cursor = self.database.cursor()
            cursor.execute(query)
            return cursor.fetchall() if fetch_all else cursor.fetchone()

        except Exception as err:
            print(err)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
