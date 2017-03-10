# from sqlalchemy import *
# from migrate import *

from sqlalchemy import Table, Column, Integer, TIMESTAMP, MetaData, Text, ForeignKey, Index, func

meta = MetaData()

data = Table(
    'data', meta,
    Column('Site_ID', Integer),
    Column('Timestamp', TIMESTAMP, default=func.now()),
    Column('Data', Text),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata

    meta.bind = migrate_engine
    data.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    data.drop()
