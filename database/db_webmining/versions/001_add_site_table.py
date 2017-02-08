# from sqlalchemy import *
# from migrate import *

from sqlalchemy import Table, Column, Integer, String, MetaData, Text

meta = MetaData()

website = Table(
    'website', meta,
	Column('Website_ID', Integer, primary_key=True),
    Column('Name', String(50), nullable=False),
    Column('Feed', Text, nullable=False),
	sqlite_autoincrement=True
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
	
	meta.bind = migrate_engine
	website.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
	meta.bind = migrate_engine
	website.drop()
	