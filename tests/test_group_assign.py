#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime as dt

import pytest

from TSGroupAssigner import GroupAssigner, DateException

# sample input
creds = {
    'host': 'localhost',
    'port': 10011,
    'user': 'serveradmin',
    'password': '5up3r_53cr37',
    'sid': 1,
    'gid': 24
}


class TestGroupAssigner:
    def test_missing_input(self):
        # the main class is missing arguments and should fail with a TypeError

        with pytest.raises(TypeError):
            GroupAssigner().start()

    def test_sleepstart_startdate(self):
        # startdate is too far in the future sleepstart should produce a DateException

        # start date 3 days in the future
        startdate = dt.date.today() + dt.timedelta(days=3)
        duration = dt.timedelta()

        with pytest.raises(DateException):
            GroupAssigner(date=startdate, delta=duration, **creds).start()

    def test_datecheck_enddate(self):
        # this should produce a exit code 0 SystemExit as the end date is in the past

        # start date 2 days in the past
        startdate = dt.date.today() + dt.timedelta(days=-2)
        duration = dt.timedelta()

        with pytest.raises(SystemExit):
            GroupAssigner(date=startdate, delta=duration, **creds).start()

    def test_connect_noconnection(self):
        # connect should fail with ConnectionRefusedError

        # start date is today
        startdate = dt.date.today()
        duration = dt.timedelta()

        with pytest.raises(ConnectionRefusedError):
            GroupAssigner(date=startdate, delta=duration, **creds).start()
