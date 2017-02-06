# from sqlalchemy import *
# from migrate import *

from sqlalchemy import Table, Column, Integer, String, MetaData, Text

meta = MetaData()

website = Table(
    'website', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('feed', Text),
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
	