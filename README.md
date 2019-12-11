# TeamSpeak GroupAssigner
[![CodeFactor](https://www.codefactor.io/repository/github/mightybroccoli/tsgroupassigner/badge)](https://www.codefactor.io/repository/github/mightybroccoli/tsgroupassigner)

## Overview
TSGroupAssigner is a module which allows to automatically assign server groups to voice clients, if they connect within 
a specified date range.

### example 
This small example could be called on the 23.12 to assign the group `24` to every voice client connecting
to the server id `1`.
The process will terminate gracefully when the configured date range is exceeded.

```python
import datetime as dt
import logging
from TSGroupAssigner import GroupAssigner

logger = logging.getLogger()
logger.setLevel(logging.INFO)

creds = {
    'host': 'localhost',
    'port': 10011,
    'user': 'serveradmin',
    'password': '5up3r_53cr37',
    'sid': 1,
    'gid': 24
}

target = dt.date(year=2019, month=24, day=12)
duration = dt.timedelta(days=2)

GroupAssigner(date=target, delta=duration, **creds).start()
```
