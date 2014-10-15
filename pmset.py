import re
import sys
import datetime
import dateutil.parser
import subprocess

PMSET_DATE_FORMAT = "%m/%d/%y %H:%M:%S"

def get_current_schedule():
    """
    Returns a list of (datetime, action) pairs in datetime order
    """
    output = subprocess.check_output(
            'pmset -g sched'.split()
        )
    print output

    sched_re = re.compile(r'.* (.*) at (.*)')
    lines = output.split('\n')[1:-1]

    events = []
    for line in lines:
        event = sched_re.search(line)
        action = event.group(1)
        event_datetime = dateutil.parser.parse(event.group(2))

        events.append({"datetime": event_datetime, "action": action})

    return sorted(events, key=lambda event: event["datetime"])

def schedule_sleep(dt):
    subprocess.call('pmset schedule sleep "%s" 2>&1' % dt.strftime(PMSET_DATE_FORMAT), shell=True)

def schedule_wake(dt):
    subprocess.call('pmset schedule wake "%s" 2>&1' % dt.strftime(PMSET_DATE_FORMAT), shell=True)

def print_schedule():
    subprocess.call('pmset -g sched', shell=True)

def cancel_wake(dt):
    subprocess.call('pmset schedule cancel wake "%s" 2>&1' % dt.strftime(PMSET_DATE_FORMAT), shell=True)

def cancel_sleep(dt):
    subprocess.call('pmset schedule cancel sleep "%s" 2>&1' % dt.strftime(PMSET_DATE_FORMAT), shell=True)

def cancel_all_events():
    events = get_current_schedule()
    for event in events:
        if event["action"] == "sleep":
            cancel_sleep(event["datetime"])
        elif event ["action"] == "wake":
            cancel_wake(event["datetime"])

def main():
    if sys.argv[1] == "cancelall":
        cancel_all_events()
    elif sys.argv[1] == "print":
        print_schedule()
    else:
        print "Usage: %s [print | cancelall]" % sys.argv[0]

if __name__ == "__main__":
    main()
