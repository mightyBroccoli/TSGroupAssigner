# TeamSpeak GroupAssigner
[![PyPI](https://img.shields.io/pypi/v/TSGroupAssigner.svg)](https://pypi.python.org/pypi/TSGroupAssigner)
[![PyPI](https://img.shields.io/pypi/pyversions/TSGroupAssigner.svg)](https://pypi.python.org/pypi/TSGroupAssigner)
[![CodeFactor](https://www.codefactor.io/repository/github/mightybroccoli/TSGroupAssigner/badge)](https://www.codefactor.io/repository/github/mightybroccoli/TSGroupAssigner)

## Overview
TSGroupAssigner is a module which allows to automatically assign server groups to voice clients, if they connect within 
a specific date range.

### example
This small example script could be called before christmas to assign the group `24` to every voice client connecting
to the server id `1`.
The process will terminate gracefully, when the configured date range is exceeded.

```python
import datetime as dt
import logging
from TSGroupAssigner import GroupAssigner, DateException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

params = {
    'host': 'localhost',
    'port': 10011,
    'user': 'serveradmin',
    'password': '5up3r_53cr37',
    'sid': 1,
    'gid': 24
}

target = dt.date(year=2020, month=2, day=14)
duration = dt.timedelta(days=2)

try:
    GroupAssigner(date=target, nick="James", delta=duration, **params).start()
except DateException as err:
    logger.error(err)
```
