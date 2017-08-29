from sqlalchemy.orm import mapper
from sqlalchemy import *
from sqlalchemy.sql import table, text
from sqlalchemy.schema import DDLElement
from sqlalchemy.ext import compiler
import datetime

from app.database import db_session
from app.models import Base

######
# Views
######

class_details = Table(
    'classdetails', Base.metadata,
    Column('ClassId', Integer, primary_key=True),
    Column('Start', DateTime),
    Column('End', DateTime),
    Column('ArchiveState', Boolean, server_default=FetchedValue()),
    Column('LecCoursePairId', Integer),
    Column('LecId', Integer),
    Column('LecName', String(60)),
    Column('CourseId', Integer, ForeignKey('courses.name', ondelete='CASCADE', onupdate='CASCADE')),
    Column('CourseName', String(60), ForeignKey('courses.name', ondelete='CASCADE', onupdate='CASCADE')),
    autoload=True,
    autoload_with=engine,
)


class ClassDetails(object):
    query = db_session.query_property()

    def __init__(self, start=datetime.datetime.now, end=None, archivedState=False, lecCoursePairId=0, lecId=0,
                 lecName='',
                 courseId=0, courseName=''):
        self.Start = start
        self.End = end
        self.ArchivedState = archivedState
        self.LecCoursePairId = lecCoursePairId
        self.LecId = lecId
        self.LecName = lecName
        self.CourseId = courseId
        self.CourseName = courseName


active_classes = Table(
    'activeclasses', Base.metadata,
    Column('ClassId', Integer, primary_key=True),
    Column('DateAndTime', DateTime),
    Column('Duration', Float, server_default=FetchedValue()),
    Column('ArchiveState', Boolean, server_default=FetchedValue()),
    Column('LecCoursePairId', Integer),
    Column('LecId', Integer),
    Column('LecName', String(60)),
    Column('CourseId', Integer, ForeignKey('courses.name', ondelete='CASCADE', onupdate='CASCADE')),
    Column('CourseName', String(60), ForeignKey('courses.name', ondelete='CASCADE', onupdate='CASCADE')),
    autoload=True,
    autoload_with=engine,
)


class ActiveClasses(object):
    query = db_session.query_property()

    def __init__(self, DateAndTime=datetime.datetime, Duration=0, ArchiveState=False, LecCoursePairId=0, LecId=0,
                 LecName='',
                 CourseId=0, CourseName=''):
        self.DateAndTime = DateAndTime
        self.Duration = Duration
        self.ArchiveState = ArchiveState
        self.LecCoursePairId = LecCoursePairId
        self.LecId = LecId
        self.LecName = LecName
        self.CourseId = CourseId
        self.CourseName = CourseName


mapper(ClassDetails, class_details)
mapper(ActiveClasses, active_classes)

metadata = MetaData(bind=engine)


class CreateView(DDLElement):
    """
    Class takes the name of the view to create
    and the fields to be selected from
    """

    def __init__(self, name, selectable, or_replace=False):
        self.name = name
        self.selectable = selectable
        self.or_replace = or_replace


class DropView(DDLElement):
    """
    Class takes the name of th view to be deleted
    """

    def __init__(self, name, if_exists=False, cascade=False):
        self.name = name
        self.if_exists = if_exists
        self.cascade = cascade


@compiler.compiles(CreateView)
def create_view_compiler(element, compiled):
    query = "CREATE "
    if element.or_replace:
        query += "OR REPLACE "
    query += "VIEW {} AS {}".format(element.name, compiled.sql_compiler.process(
        element.selectable
    ))
    return query


@compiler.compiles(DropView)
def drop_view_compiler(element):
    query = "DROP VIEW "
    if element.if_exists:
        query += "IF EXISTS "
    query += "{}".format(element.name)


def view(view_name, metadatas, selectable):
    """
    Method to interface with creation and dropping of view
    :param view_name: Name of view
    :param metadatas: Metadata of the database
    :param selectable: Fields to be selected from
    :return:
    """
    view_table = table(view_name)

    for c in selectable.c:
        # noinspection PyProtectedMember
        c._make_proxy(view_table)

    # create view after creating source table(s)
    CreateView(view_name, selectable, True).execute_at(event_name="after-create", target=metadatas)
    # delete view before deleting source table(s)
    DropView(view_name, if_exists=True, cascade=True).execute_at("before-drop", metadatas)
    return view_table


def create_view(view_name='', definition=''):
    """
    Method creates or replaces view using given commands
    :param view_name: Name of the view to be created
    :param definition: Commands to follow to create view
    :return:
    """
    _view = Table(view_name, MetaData(engine))
    definition = text(definition)
    CreateView(_view, definition, or_replace=True).compile()


def drop_view(view_name=''):
    """
    Method that deletes an existing view
    :param view_name: Name of view
    :return:
    """
    _view = Table(view_name, metadata)
    DropView(_view, if_exists=True, cascade=True).compile()

