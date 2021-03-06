#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from collections import defaultdict


def _class(db, lang):
    sql = """
    SELECT
        item,
        class,
        title,
        level,
        tags
    FROM
        class
    ORDER BY
        item,
        class
    """
    db.execute(sql)
    return map(lambda r: dict(zip(["item", "class", "title", "level", "tags"], r)), db.fetchall())


def _items(db, lang):
    sql = """
    SELECT
        item,
        menu
    FROM
        dynpoi_item
    ORDER BY
        item
    """
    db.execute(sql)
    return db.fetchall()


def _countries(db, lang):
    sql = """
    SELECT DISTINCT
        country
    FROM
        source
    ORDER BY
        country
    """
    db.execute(sql)
    return db.fetchall()

def _countries_3(db):
    sql = """
    SELECT DISTINCT
        country
    FROM
        source
    ORDER BY
        country
    """
    db.execute(sql)
    return map(lambda x: x[0], db.fetchall())


def _categories(db, lang):
    sql = """
    SELECT
        dynpoi_categ.categ,
        dynpoi_categ.menu AS categ_menu,
        dynpoi_item.item,
        dynpoi_item.menu,
        dynpoi_item.marker_color,
        dynpoi_item.marker_flag,
        dynpoi_item.levels,
        dynpoi_item.number,
        dynpoi_item.tags
    FROM
        dynpoi_categ
        JOIN dynpoi_item ON
            dynpoi_categ.categ = dynpoi_item.categ
    WHERE
        NOT dynpoi_item.levels = '{}'
    ORDER BY
        categ,
        item
    """
    result = []
    db.execute(sql)
    for res in db.fetchall():
        if result == [] or result[-1]["categ"] != res["categ"]:
            ret = {"categ":res["categ"], "menu": "no translation", "item": []}
            result.append(ret)
            ret["menu_lang"] = {k: v for k, v in res["categ_menu"].iteritems() if v}
            for l in lang:
                if l in res["categ_menu"]:
                    ret["menu"] = res["categ_menu"][l]
                    break
        ret["item"].append({"item":res["item"], "menu":"no translation", "marker_color":res["marker_color"], "marker_flag":res["marker_flag"], "levels":res["levels"], "number":res["number"], "tags":res["tags"]})
        for l in lang:
            if res["menu"] and l in res["menu"]:
                ret["item"][-1]["menu"] = res["menu"][l]
                break

    return result

def _items_3(db):
    sql = """
    SELECT
        dynpoi_categ.categ,
        dynpoi_categ.menu
    FROM
        dynpoi_categ
    ORDER BY
        categ
    """
    db.execute(sql)
    categs = map(lambda r: dict(zip(['categ', 'title'], r)), db.fetchall())

    sql = """
    SELECT
        item,
        categ,
        marker_color,
        menu,
        levels,
        number,
        tags
    FROM
        dynpoi_item
    ORDER BY
        item
    """
    db.execute(sql)
    items = map(lambda r: dict(zip(['item', 'categ', 'color', 'title', 'levels', 'number', 'tags'], r)), db.fetchall())
    items = map(lambda r: {
        'item': r['item'],
        'categ': r['categ'],
        'color': r['color'],
        'title': r['title'] or {'en': '(name missing)'},
        'levels': r['number'] and map(lambda (l, n): {'level': l, 'count': n}, zip(r['levels'], r['number'])) or map(lambda i: {'level': i, 'count': 0}, [1, 2, 3]),
        'tags': r['tags']
    }, items)
    items_categ = defaultdict(list)
    for i in items:
        items_categ[i['categ']].append(i)

    sql = """
    SELECT
        item,
        class,
        title,
        level,
        tags
    FROM
        class
    ORDER BY
        item,
        class
    """
    db.execute(sql)
    classs = map(lambda r: dict(zip(['item', 'class', 'title', 'level', 'tags'], r)), db.fetchall())
    class_item = defaultdict(list)
    for c in classs:
        class_item[c['item']].append(c)

    return map(lambda categ:
        dict(
            categ,
            **{'items': map(lambda item:
                dict(
                    item,
                    **{'class': class_item[item['item']]}),
                items_categ[categ['categ']])}
        ),
        categs)


def _tags(db):
    sql = """
    SELECT DISTINCT
        tag
    FROM
        (
        SELECT
            unnest(tags) AS tag
        FROM
            class
        ) AS t
    WHERE
        tag != ''
    ORDER BY
        tag
    """
    db.execute(sql)
    return map(lambda x: x[0], db.fetchall())
