# from sqlalchemy import *
# from migrate import *

from sqlalchemy import Table, Column, Integer, String, MetaData, Text, ForeignKey, Index

meta = MetaData()

link = Table(
    'link', meta,
    Column('Site_ID', Integer, primary_key=True),
	Column('Website_ID', Integer),
    Column('URL', String(50), nullable=False),
    Column('Last_Data', Text),
	sqlite_autoincrement=True
)

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
	
	meta.bind = migrate_engine
	link.create()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
	meta.bind = migrate_engine
	link.drop()
	