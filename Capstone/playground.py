from flask import Flask, jsonify, request,Blueprint
from sqlalchemy import Integer

from Capstone.models import Playground,History,ZoneHistory, ZoneStatistics
from . import db, ma
from . import mysql
import MySQLdb
import json
from .__init__ import create_app
from .wraps import token_required
from flask_cors import cross_origin
import datetime

playground = Blueprint('playground', __name__)


db.create_all(app = create_app())

class PlaygroundSchema(ma.Schema):
    class Meta:
        fields = ('id','tracking','crate_label','stacked','width','zone_id','length','x','y','rotation')

playground_schema = PlaygroundSchema()
playgrounds_schema = PlaygroundSchema(many=True)

#Outbound
@playground.route('/<zoneid>/<label>',methods=['DELETE'])
@cross_origin()
@token_required
def outbounce(current_user, token,zoneid,label):
    print(label)
    label = str(label).strip()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT stacked, width, length, x, y FROM `playground` where crate_label = %s', [label])
    crate = cursor.fetchone()
    stacked = str(crate.get('stacked'))
    width = float(crate.get('width'))
    length = float(crate.get('length'))
    x = float(crate.get('x'))
    y = float(crate.get('y'))
    
    #zone statistic
    cursor.execute('SELECT total_space, total_used, usable, number_crates, number_stacks, number_singles from `zone_statistics` where zone_id = %s', [zoneid])
    zone_statistic = cursor.fetchone()
    totalSpace = float(zone_statistic.get('total_space'))
    totalUsed = float(zone_statistic.get('total_used'))
    usableSpace = float(zone_statistic.get('usable'))
    numberCrates = int(zone_statistic.get('number_crates'))
    numberStackes = int(zone_statistic.get('number_stacks'))
    numberSingles = int(zone_statistic.get('number_singles'))

    if stacked == 'Yes':
        width = float(width) + 0.45
        length = float(length) + 0.45
        area = width * length
        usableSpace = usableSpace + area
        totalUsed = totalUsed - area
        numberCrates -= 1
        numberStackes -= 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_stacks`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberStackes,zoneid])
        mysql.connection.commit()
    else:
        width = float(width) + 0.25
        length = float(length) + 0.25
        area = width * length
        usableSpace = usableSpace + area
        totalUsed = totalUsed - area
        numberCrates -= 1
        numberSingles -= 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_singles`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberSingles,zoneid])
        mysql.connection.commit()


    cursor.execute('DELETE FROM `playground` WHERE zone_id = %s AND crate_label = %s',[zoneid,label])
    items=cursor.fetchall()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT zone_name FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    zname=cursor.fetchone()
    zonename=str(zname.get('zone_name'))
    Zonehistory = ZoneHistory(zoneid,"Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    history = History("Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    db.session.add(Zonehistory)
    db.session.add(history)
    mysql.connection.commit()
    cursor.close()
    return jsonify({"Message":"item was successfully deleted"})

#inbound
@playground.route('/<zoneid>',methods=['POST'])
@cross_origin()
@token_required
def add_item(current_user, token,zoneid):
    req_data = request.get_json(force=False, silent=False, cache=True)
    user_id = current_user.user_id
    user_id = user_id
    print(type(zoneid))
    zone_id = int(zoneid)
    crate_label = req_data['crate_label']
    tracking = req_data['tracking']
    stacked = req_data['stacked']
    width = req_data['width']
    length = req_data['length']
    x = req_data['x']
    y = req_data['y']
    rotation = req_data['rotation']
    print("zone id: "+ str(zone_id))

    playground = Playground(tracking,crate_label,stacked,width,length,zone_id,x,y,rotation)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT zone_name FROM `refreshed_zones` WHERE zone_id = %s',[zoneid])
    zname=cursor.fetchone()
    zonename=str(zname.get('zone_name'))
    #zone statistic
    cursor.execute('SELECT total_space, total_used, usable, number_crates, number_stacks, number_singles from `zone_statistics` where zone_id = %s', [zoneid])
    zone_statistic = cursor.fetchone()
    totalSpace = float(zone_statistic.get('total_space'))
    totalUsed = float(zone_statistic.get('total_used'))
    usableSpace = float(zone_statistic.get('usable'))
    numberCrates = int(zone_statistic.get('number_crates'))
    numberStackes = int(zone_statistic.get('number_stacks'))
    numberSingles = int(zone_statistic.get('number_singles'))
    
    if stacked == 'Yes':
        width = float(width) + 0.45
        length = float(length) + 0.45
        area = width * length
        usableSpace = usableSpace - area
        totalUsed = totalUsed + area
        numberCrates += 1
        numberStackes += 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_stacks`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberStackes,zoneid])
        mysql.connection.commit()
    else :
        width = float(width) + 0.25
        length = float(length) + 0.25
        area = width * length
        usableSpace = usableSpace - area
        totalUsed = totalUsed + area
        numberCrates += 1
        numberSingles += 1
        cursor.execute('UPDATE `zone_statistics` SET `total_used`=%s,`usable`=%s,`number_crates`=%s,`number_singles`=%s WHERE zone_id = %s',[totalUsed,usableSpace,numberCrates,numberSingles,zoneid])
        mysql.connection.commit()


    Zonehistory = ZoneHistory(zoneid,"Upload New Layout for Zone: "+zonename,user_id,datetime.datetime.utcnow())
    history = History("Upload New Layout for Zone: "+zonename,current_user.user_id,datetime.datetime.utcnow())
    db.session.add(Zonehistory)
    db.session.add(history)
    db.session.add(playground)
    db.session.commit()
    return playground_schema.jsonify(playground)

@playground.route('/zoneid=<id>',methods =['GET'])
@cross_origin()
@token_required
def playgroundbyid(current_user, token, id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT l.* FROM playground l WHERE l.zone_id = %s;",[id])
    all_projects = cursor.fetchall()
    cursor.close()
    results = json.dumps(all_projects)
    return results