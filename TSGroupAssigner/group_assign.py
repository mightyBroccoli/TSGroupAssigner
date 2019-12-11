#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime as dt
import logging
import sys
import time

import ts3


class DateException(Exception):
    """raise this if the date delta exceeds the configured range"""


class GroupAssigner:
    def __init__(self, host: str, port: (str, int), user: str, password: str, sid: (str, int), gid: (str, int),
                 date: dt.date, delta: dt.timedelta):
        # host config
        self.host = host
        self.port = port
        self.user = user
        self.pw = password
        self.sid = sid

        # group
        self.gid = gid

        # start date and delta
        self.sleepstart = date - dt.timedelta(days=1)
        self.startdate = date
        self.enddate = date + delta
        self.delta = delta

    def __connect(self):
        """
        establish query connection and return connection handler
        """
        try:
            # connect to the telnet interface
            self.conn = ts3.query.TS3Connection(self.host, self.port)

            # login
            self.conn.login(client_login_name=self.user, client_login_password=self.pw)

            # select specified sid
            self.conn.use(sid=self.sid)

        # break if credentials are invalid
        except ts3.query.TS3QueryError as TS3QueryError:
            # log error line and reraise
            logging.error(TS3QueryError)
            raise TS3QueryError

    def __disconnect(self):
        """
        method to gracefully logout and disconnect the connection
        this should only be called if the exit is intentional
        """
        try:
            self.conn.logout()
            self.conn.quit()

        # attribute error if disconnect is called prior to the connection being established
        except AttributeError:
            pass

        # broad exception if something unexpected happens
        except ts3.TS3Error as TS3Error:
            # log error and reraise exception
            logging.error(TS3Error)
            raise TS3Error

        # exit
        sys.exit()

    def __datecheck(self):
        """
        method to check if the current date is still in the configured date range
        """
        now = dt.date.today()

        # check if target date is in the configured range
        if self.startdate <= now <= self.enddate:
            logging.debug('target date within configured date range')
            return True

        # if date range is exceeded shutdown gracefully
        else:
            # terminate possible open connections
            logging.info('the current date exceeds the configured date range -- exiting')
            self.__disconnect()

    def __sleepstart(self):
        """
        method to check if the process is eligible to sleepstart
        """
        now = dt.date.today()

        # start date already reached proceed
        if self.startdate <= now:
            logging.debug('start date is already reached -- not eligible to sleepstart continue')
            return

        # if startdate within the next 24h proceed to sleepstart
        elif now >= self.startdate - dt.timedelta(days=1):
            # convert both dates to datetime
            starttime = dt.datetime.combine(self.startdate, dt.time(hour=0, minute=0, second=0))
            now = dt.datetime.now()

            # calculate remaining time delta
            remaindelta = starttime - now
            logging.debug('target date will be reached in {sec} seconds -- sleeping'.format(sec=remaindelta.seconds))
            time.sleep(remaindelta.seconds + 1)

        # if the date is too far back raise DateException
        else:
            raise DateException('target date is too far in the future')

    def start(self):
        # eol to start process ahead of time
        self.__sleepstart()

        # proceed only if target date is inside the date range
        if self.__datecheck():
            # init connection
            self.__connect()

            # start processing
            self.__main()

    def __main(self):
        # register for "server" notify event
        self.conn.servernotifyregister(event="server")

        # start listening and processing
        while True:
            self.conn.send_keepalive()

            try:
                # wait for an event to be thrown
                event = self.conn.wait_for_event(timeout=60)

            # process TeamSpeak Telnet timeout
            except ts3.query.TS3TimeoutError:
                pass

            else:
                # only parse entering clients info
                if event.event == "notifycliententerview":
                    # is the event still eligible
                    self.__datecheck()

                    # skip query clients -- query client = 1 , voice client = 0
                    if event[0]['client_type'] == '0':

                        # reasonid should be 0 not sure why though
                        if event[0]["reasonid"] == "0":

                            cldbid = event.parsed[0]['client_database_id']
                            user_grps = event.parsed[0]['client_servergroups'].split(sep=',')

                            msg = '{client_nickname}:{client_database_id} connected - member of {client_servergroups}'
                            logging.debug(msg.format(**event[0]))

                            # only try to add nonmembers to group
                            if str(self.gid) not in user_grps:

                                # https://yat.qa/ressourcen/server-query-kommentare/
                                # Usage: servergroupaddclient sgid={groupID} cldbid={clientDBID}
                                try:
                                    cmd = self.conn.servergroupaddclient(sgid=self.gid, cldbid=cldbid)

                                    if cmd.error['id'] != '0':
                                        logging.error(cmd.data[0].decode("utf-8"))

                                    # log process
                                    msg = '{client_nickname}:{client_database_id} added to {gid}'
                                    logging.info(msg.format(**event[0], gid=self.gid))

                                # log possible key errors while the teamspeak 5 client is not fully working
                                except KeyError:
                                    logging.error(str(event.parsed))
                                    pass