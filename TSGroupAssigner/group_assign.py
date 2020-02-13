#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime as dt
import logging
import sys
import time
from contextlib import suppress

import ts3

from .exceptions import DateException

__all__ = ['GroupAssigner']


class GroupAssigner:
    def __init__(self, host: str, port: (str, int), user: str, password: str, sid: (str, int), gid: (str, int),
                 date: dt.date, nick: (str, int) = None, delta: dt.timedelta = dt.timedelta(days=0)):
        # host config
        self.host = host
        self.port = port
        self.user = user
        self.pw = password

        # server and group id
        self.nick = nick
        self.sid = sid
        self.gid = gid

        # start date and delta
        self.sleepstart = date - dt.timedelta(days=1)
        self.startdate = date
        self.enddate = date + delta

        # init connection handler
        self.conn = None

    def __connect(self):
        """ establish query connection and return connection handler """
        # connect to the telnet interface
        self.conn = ts3.query.TS3Connection(self.host, self.port)

        # login
        self.conn.login(client_login_name=self.user, client_login_password=self.pw)

        # select specified sid
        self.conn.use(sid=self.sid)

        # assign friendly nickname
        self.__set_botname(self.nick)

    def __disconnect(self):
        """ gracefully logout and disconnect the connection, this should only be called if the exit is intentional """
        try:
            self.conn.logout()
            self.conn.quit()

        # attribute error if disconnect is called prior to the connection being established
        except AttributeError:
            pass

        # broad exception if something unexpected happens
        except ts3.TS3Error as err:
            # log exception
            logging.error(err)

        # exit
        sys.exit()

    def __checkdate(self):
        """ method to check if the current date is still in the configured date range """
        now = dt.date.today()

        # check if still in the configured range
        if not self.startdate <= now <= self.enddate:
            # if date range is exceeded shutdown gracefully
            logging.info('the current date exceeds the configured date range -- exiting')
            self.__disconnect()

        # else continue
        logging.debug('heartbeat - target date within configured date range')

    def __start_sleepstart(self):
        """ method to check if the process is eligible to sleepstart """
        now = dt.date.today()

        # start date already reached proceed
        if self.startdate <= now:
            logging.debug('start date is already reached -- not eligible to sleepstart continue')

        # if startdate within the next 24h proceed to sleepstart
        elif now >= self.startdate - dt.timedelta(days=1):
            # convert both dates to datetime
            starttime = dt.datetime.combine(self.startdate, dt.time(hour=0, minute=0, second=0))
            now = dt.datetime.now()

            # calculate remaining time delta
            remaindelta = starttime - now
            logging.debug(f'target date will be reached in {remaindelta.seconds} seconds -- sleeping')
            time.sleep(remaindelta.seconds + 1)

        else:
            # if the date is too far back raise DateException
            raise DateException('target date is too far in the future')

    def __set_botname(self, nickname: (str, int)):
        """
        method setting the bots client_nickname
        @param nickname: nickname for the bot
        """
        # none catch
        if nickname is not None:
            client_nick = nickname

        # default to project name # TODO better default name
        else:
            client_nick = 'TSGroupAssigner'

        # set nickname
        self.conn.clientupdate(client_nickname=client_nick)

    def __assigngroup(self, cldbid: str, client_nickname: str, client_servergroups: str):
        """
        method to assign the specified client_database_id the defined group
        @param cldbid: client_database_id uniquely assigned to each user
        @param client_servergroups: list of groups the client is a member of
        @param client_nickname: username to the cldbid
        """
        # only try to add nonmembers to group
        if str(self.gid) not in client_servergroups.split(sep=','):
            logging.debug(f'{client_nickname}:{cldbid} is not member of {self.gid}')

            try:
                # Usage: servergroupaddclient sgid={groupID} cldbid={clientDBID}
                cmd = self.conn.servergroupaddclient(sgid=self.gid, cldbid=cldbid)

                if cmd.error['id'] != '0':
                    logging.error(cmd.data[0].decode("utf-8"))

                # log process
                logging.info(f'add {client_nickname}:{cldbid} to {self.gid}')

            # log possible key errors while the teamspeak 5 client is not fully released
            except KeyError as err:
                logging.error(err)

    def __clientlist(self, data: list):
        """
        handler for the currently connected clients
        @param data: list containing users info as dictionaries
        """

        for user in data:
            # only proceed if its a voice client
            if user['client_type'] != '0':
                continue

            # query the client info as clientlist does not return group info
            clid = user['clid']
            user_info = self.conn.clientinfo(clid=clid).parsed[0]

            # assign necessary info
            cldbid = user_info['client_database_id']
            client_servergroups = user_info['client_servergroups']
            client_nickname = user_info['client_nickname']

            # logging is key
            logging.debug(f'{client_nickname}:{cldbid} is online - member of {client_servergroups}')

            # hand over necessary info to the assignment method
            self.__assigngroup(cldbid=cldbid, client_nickname=client_nickname, client_servergroups=client_servergroups)

    def __notifycliententerview(self, data: dict):
        """
        event thrown if a client connects to the server
        :param data: dictionary containing users info
        """
        # return all non voice clients without reasonid 0
        if data['client_type'] != '0' or data['reasonid'] != '0':
            return

        cldbid = data['client_database_id']
        client_servergroups = data['client_servergroups']
        client_nickname = data['client_nickname']

        logging.debug(f'{client_nickname}:{cldbid} connected - member of {client_servergroups}')

        # hand over necessary info to the assignment method
        self.__assigngroup(cldbid=cldbid, client_nickname=client_nickname, client_servergroups=client_servergroups)

    def __handle_event(self, event: str, data: (dict, list)):
        """ event handler which separates events to their specific handlers """
        # check if event is still eligible
        self.__checkdate()

        # client enter events
        if event == "notifycliententerview":
            self.__notifycliententerview(data)

        if event == "clientlist":
            self.__clientlist(data)

    def start(self):
        """ main entry point to start the bot """
        # eol to start process ahead of time
        self.__start_sleepstart()

        # proceed only if target date is inside the date range
        self.__checkdate()

        try:
            # init connection
            self.__connect()

        # break if credentials are invalid
        except ts3.query.TS3QueryError as err:
            # log error and disconnect
            logging.error(err)
            self.__disconnect()

        # start processing
        self.__main()

    def __main(self):
        """ main loop """
        # register for "server" notify event
        self.conn.servernotifyregister(event="server")

        # handle already connected clients
        cl_list = self.conn.clientlist(voice=True).parsed
        self.__handle_event("clientlist", cl_list)

        # start listening and processing
        while True:
            self.conn.send_keepalive()

            # suppress TimeoutError exceptions
            with suppress(ts3.query.TS3TimeoutError):
                # wait for events
                event = self.conn.wait_for_event(timeout=60)

                # handover event to eventhandler
                self.__handle_event(event.event, event.parsed[0])
