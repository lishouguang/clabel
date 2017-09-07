# coding: utf-8

import logging
import sqlite3

from clabel.helper import utils
from clabel.config import DB_FILE

CREATE_POLAR_SQL = '''
create table if not exists polar(
  id integer primary key autoincrement,
  context varchar(128),
  opinion varchar(128),
  polar varchar(2)
)
'''

logger = logging.getLogger(__file__)

with sqlite3.connect(DB_FILE) as _conn:
    _conn.isolation_level = None
    _conn.execute(CREATE_POLAR_SQL)


def insertOrUpdate(context, opinion, polar):
    context = utils.convert2unicode(context)
    opinion = utils.convert2unicode(opinion)
    polar = utils.convert2unicode(polar)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("select count(1) from polar where context=? and opinion=?", (context, opinion))
        if int(cursor.fetchone()[0]) > 0:
            logger.debug('update polar set polar=%s where context=%s and opinion=%s', polar, context, opinion)
            cursor.execute("update polar set polar=? where context=? and opinion=?", (polar, context, opinion))
        else:
            logger.debug('insert into polar(context, opinion, polar) values (%s, %s, %s)', context, opinion, polar)
            conn.execute("insert into polar(context, opinion, polar) values (?, ?, ?)", (context, opinion, polar))
        conn.commit()


def query(context, opinion):
    context = utils.convert2unicode(context)
    opinion = utils.convert2unicode(opinion)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("select polar from polar where context=? and opinion=?", (context, opinion))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


def queryAll():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("select context, opinion, polar from polar")
        return [(r[0], r[1], r[2]) for r in cursor.fetchall()]


def delete(context, opinion):
    context = utils.convert2unicode(context)
    opinion = utils.convert2unicode(opinion)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("delete from polar where context=? and opinion=?", (context, opinion))

