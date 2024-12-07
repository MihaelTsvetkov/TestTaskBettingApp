from databases import Database
from config import settings

database = Database(settings.DATABASE_URL)

print("DATABASE URL: ", settings.DATABASE_URL)