#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

import ts3

from config import Config


def watcher(conn):
    # Register for events
    # https://yat.qa/ressourcen/server-query-notify/#server
    conn.servernotifyregister(event="server")

    while True:
        conn.send_keepalive()

        try:
            event = conn.wait_for_event(timeout=60)

        except ts3.query.TS3TimeoutError:
            pass

        else:
            # only parse entering clients info
            if event.event == "notifycliententerview":

                # skip query clients -- query client = 1 , voice client = 0
                if event[0]['client_type'] == '0':

                    # reasonid should be 0 not sure though
                    if event[0]["reasonid"] == "0":

                        user_grps = event.parsed[0]['client_servergroups'].split(sep=',')
                        gid = Config.GID

                        # only try to add nonmembers to group
                        if str(gid) not in user_grps:

                            cldbid = event.parsed[0]['client_database_id']

                            # https://yat.qa/ressourcen/server-query-kommentare/
                            # Usage: servergroupaddclient sgid={groupID} cldbid={clientDBID}
                            try:
                                cmd = conn.servergroupaddclient(sgid=gid, cldbid=cldbid)

                                if cmd.error['id'] != '0':
                                    logger.info(cmd.data[0].decode("utf-8"))

                                # log process
                                logmsg = '{client_nickname}:{client_database_id} - added to {gid}'
                                logging.info(logmsg.format(**event[0], gid=gid))

                            except KeyError:
                                logger.error(str(event.parsed))
                                pass


if __name__ == "__main__":
    # logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logf = logging.FileHandler('info.log')
    logf.setFormatter(logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s"))

    logger.addHandler(logf)

    with ts3.query.TS3Connection(Config.HOST, Config.PORT) as ts3conn:
        ts3conn.login(client_login_name=Config.USER, client_login_password=Config.PW)
        ts3conn.use(sid=Config.SID)
        watcher(ts3conn)
