from migrate import *
from sqlalchemy import Table, MetaData, String, Column, TIMESTAMP

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData(bind=migrate_engine)
    link = Table('link', meta, autoload=True)
    createdC = Column('created', TIMESTAMP)

    createdC.create(link)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    link = Table('link', meta, autoload=True)

    link.c.created.drop()
