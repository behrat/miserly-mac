import re
import sys
import datetime
import dateutil.parser
import subprocess
import pmset
import RTPscrape

PRICE_CUTOFF = .040
SLEEP_EARLY_MIN = 12
WAKE_LATE_MIN = 1

now = datetime.datetime.now()
today = datetime.date.today()

if now.hour < 17: 
    querydate = today
else:
    querydate = today + datetime.timedelta(days=1)

period_prices = RTPscrape.get_prices_for_day(querydate)

# We must be awake to run this script
sleeping = False

current_sched = pmset.get_current_schedule()
events = iter(current_sched)

next_event = next(events, None)

for period_price in period_prices:

    price = period_price["price"]
    sleep_time = period_price["start"] - datetime.timedelta(minutes=SLEEP_EARLY_MIN)
    wake_time = period_price["start"] - datetime.timedelta(minutes=WAKE_LATE_MIN)

    if sleeping:
        next_potential_event = wake_time
    else:
        next_potential_event = sleep_time

    while next_event is not None and next_event["datetime"] <= next_potential_event:
        if next_event["action"] == "sleep":
            sleeping = True
        elif next_event["action"] == "wake":
            sleeping = False
        next_event = next(events, None)

        if sleeping:
            next_potential_event = wake_time
        else:
            next_potential_event = sleep_time

    if not sleeping:
        if price >= PRICE_CUTOFF:
            sleeping = True
            # TODO: handing beginning of day
            print "Scheduling Sleep"
            pmset.schedule_sleep(sleep_time)

    if sleeping:
        if price < PRICE_CUTOFF:
            sleeping = False
            print "Scheduleing Wake"
            pmset.schedule_wake(wake_time)

    print period_price["start"]

pmset.print_schedule()
