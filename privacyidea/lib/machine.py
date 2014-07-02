# -*- coding: utf-8 -*-
#
#  privacyIDEA
#  June 30, 2014 Cornelius Kölbel, info@privacyidea.org
#  http://www.privacyidea.org
#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from privacyidea import model
from privacyidea.model import Machine, MachineToken, MachineOptions
from privacyidea.model.meta import Session
from privacyidea.lib.token import getTokens4UserOrSerial
from sqlalchemy import and_

import logging
log = logging.getLogger(__name__)
from privacyidea.lib.log import log_with

@log_with(log)
def create(name, ip=None, desc=None, decommission=None):
    machine = Machine(name, ip=ip, desc=desc, decommission=decommission)
    machine.store()
    log.info("Machine %r created." % machine)
    return machine

@log_with(log)
def delete(name):
    '''
    Delete the machine with the name and return the number of deleted machines
    
    Should always be 1
    Should be 0 if such a machine did not exist.
    '''
    num = Session.query(Machine).filter(Machine.cm_name == name).delete()
    Session.commit()
    # 1 -> success
    return num == 1
    
@log_with(log)    
def show(name=None):
    res = {}
    if name:
        sqlquery = Session.query(Machine).filter(Machine.cm_name == name)
    else:
        sqlquery = Session.query(Machine)
    for machine in sqlquery:
        res[machine.cm_name] = machine.to_json()
    return res

def _get_machine_id(machine_name):
    # determine the machine_id for the machine name
    machine = show(machine_name)
    machine_id = machine.get("tokenmachine",{}).get("id")
    return machine_id

def _get_token_id(serial):
    # determine the token_id for the serial
    tokenlist = getTokens4UserOrSerial(serial=serial)
    if len(tokenlist) == 0:
        raise Exception("There is no token with the serial number %r" % serial)
    
    token_id = tokenlist[0].token.privacyIDEATokenId
    return token_id


@log_with(log)
def addtoken(machine_name, serial, application):
    machine_id = _get_machine_id(machine_name)
    token_id = _get_token_id(serial)
    machinetoken = MachineToken(machine_id, token_id, application)
    machinetoken.store()
    return machinetoken

@log_with(log)
def deltoken(machine_name, serial, application):
    machine_id = _get_machine_id(machine_name)
    token_id = _get_token_id(serial)
    
    num = Session.query(MachineToken).filter(and_(MachineToken.token_id == token_id,
                                             MachineToken.machine_id == machine_id,
                                             MachineToken.application == application)).delete()
    Session.commit()
    # 1 -> success
    return num == 1
    
    
@log_with(log)
def showtoken(machine_name=None, serial=None, application=None):
    res = {}
    machine_id = None
    token_id = None
    condition = None
    
    if machine_name:
        machine_id = _get_machine_id(machine_name)
    if serial:
        token_id = _get_token_id(serial)
    
    if machine_id:
        condition = and_(condition, MachineToken.machine_id == machine_id)
    if token_id:
        condition = and_(condition, MachineToken.token_id == token_id)
    if application:
        condition = and_(condition, MachineToken.application == application)
    
    sqlquery = Session.query(MachineToken).filter(condition)
    for row in sqlquery:
        res[row.id] = row.to_json()
    return res

