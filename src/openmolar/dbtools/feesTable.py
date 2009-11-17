# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import sys
from openmolar.connect import connect
from openmolar.settings import localsettings

private_only = False
nhs_only = False

newfeetable_Headers = "section,code,oldcode,USERCODE,regulation," + \
"description,description1,NF08,NF08_pt,NF09,NF09_pt,PFA"


def getFeeHeaders():
    return newfeetable_Headers.split(",")[1:]

def getFeeDict():
    '''
    returns a dictionary of lists of tuples (!)
    dict[section]=feedict
    feedict=[(code1,desc1,fees1),(code2,desc2,fees2)]
    '''
    option=""
    if private_only:
        option += "where PFA>0"
    elif nhs_only:
        option += "where (NF08>0 or NF09>0)"

    db=connect()
    cursor=db.cursor()
    
    query = 'select %s from newfeetable %s' % (
    newfeetable_Headers,option)

    cursor.execute(query)
    feescales = cursor.fetchall()
    cursor.close()

    sections={}

    for row in feescales:
        if not sections.has_key(row[0]):
            sections[row[0]]=[]
        sections[row[0]].append(row[1:])
    return sections

def getFeeDictForModification():
    '''
    a comprehensive dictionary formed from the entire table in the database
    '''
    global feeDict_dbstate
    db = connect()
    cursor = db.cursor()
    cursor.execute('select ix,%s from newfeetable'% newfeetable_Headers)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()

    feeDict = {}

    for row in rows:
        feeDict[row[0]] = row
    
    return feeDict

def updateFeeTable(feeDict, changes):
    '''
    pass a feeDict, and update the existing table with it.
    '''
    print "applying changes to feeTable", changes
    try:
        db = connect()
        cursor = db.cursor()
        columnNo = len(feeDict[feeDict.keys()[0]])
        valuesString = "%s," * columnNo
        valuesString = valuesString.strip(",")
        
        delquery = "delete from newfeetable where ix = %s"
        query = "insert into newfeetable (ix,%s) values (%s)"% (
        newfeetable_Headers, valuesString) 
            
        for key in changes:
            cursor.execute(delquery, key)
            print query, feeDict[key]
            cursor.execute(query, feeDict[key])

        cursor.close()        
        db.commit()
        return True
    except Exception, e:
        print "exception",e
        return False
    
def decode(blob):
    '''
    decode in blocks of 4 bytes - this is a relic from the old database
    '''
    i=0
    retlist=[]
    for i in range(0,len(blob),4):
        cost=struct.unpack_from('H',blob,i)[0]
        retlist.append(cost)
    return retlist


def feesHtml():
    return toHtml(getFees())

if __name__ == "__main__":
    #localsettings.initiate(False)
    #print localsettings.privateFees
    #print getFeeDict()
    fd = getFeeDictForModification()
    #fd[1] = (1,1, '0101', '1a', 'CE', '', 'Clinical Examination^', 'clinical exam', 801, 2, 803,4, 1951)
    #updateFeeTable(fd,[1])