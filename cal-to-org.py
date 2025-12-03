import datetime
import pytz
import os
import configparser
from Foundation import NSDateFormatter
from CalendarStore import CalCalendarStore, EKEventStore



def get_one_on_one_partner(event, self_email=None):
    attendees = event.attendees()
    if not attendees:
        return None

    # Normalize self email once
    self_email = self_email.lower() if self_email else None

    humans = []

    for a in attendees:
        try:
            name = a.name()
        except:
            name = None

        try:
            email = str(a.URL().resourceSpecifier()).lower() if a.URL() else None
        except:
            email = None

        # Exclude yourself
        if self_email and email and self_email == email:
            continue

        # Exclude rooms: heuristic
        role = None
        try:
            role = a.participantRole()
        except:
            pass

        # Role filtering: 3 is often "room" or "non-person" in EventKit
        if role == 3:
            continue

        # Fallback: if email or name looks like a resource
        if email and any(x in email for x in ["resource", "room", "conf", "meeting"]):
            continue
        if name and name.lower() in ["room", "meeting room"]:
            continue

        humans.append(name or email)

    # Accept only if exactly one human remains
    if len(humans) == 1:
        return humans[0]

    return None


def get_calendar_events(config):
    store = CalCalendarStore.defaultCalendarStore()
    calendars = [config['Main']['calendar']]
    # Define the date range: Today to 14 days from now
    dateFormat = NSDateFormatter.alloc().init()
    dateFormat.setDateFormat_('yyyyMMdd HH:mm')
    start_date = dateFormat.dateFromString_(datetime.datetime.now().strftime('%Y%m%d %H:%M'))
    end_date = start_date.dateByAddingTimeInterval_(
        14 * 24 * 60 * 60
    )
    # Construct a predicate to fetch events within the range
    store = EKEventStore.alloc().init()
    calendars_array = [calendar for calendar in store.calendars() if str(calendar.title()) in calendars]
    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(start_date, end_date, calendars_array)
    events = store.eventsMatchingPredicate_(predicate)
    return events


def get_availability_string(availability):
    mapping = {
        0: "Busy",
        1: "Busy",
        2: "Free",
        3: "Tentative",
        4: "Unavailable"
    }

    return mapping.get(availability, "Unknown")

# Adapted from ews-orgmode
def format_orgmode_date(dateObj):
  return dateObj.strftime("%Y-%m-%d %H:%M")

# Adapted from ews-orgmode
def format_orgmode_time(dateObj):
  return dateObj.strftime("%H:%M")

# Helper function to write an orgmode entry
# Adapted from ews-orgmode
def print_orgmode_entry(subject, start, end, location, response, partner=None):

  startDate = start;
  endDate = end;
  # Check if the appointment starts and ends on the same day and use proper formatting
  dateStr = ""
  if startDate.date() == endDate.date():
    dateStr = "<" +  format_orgmode_date(startDate) + "-" + format_orgmode_time(endDate) + ">"
  else:
    dateStr = "<" +  format_orgmode_date(startDate) + ">--<" + format_orgmode_date(endDate) + ">"

  if subject is not None:
    if dateStr != "":
      print("* " + dateStr + " " + subject)
    else:
      print("* " + subject)

  if location is not None or partner is not None:
    print(":PROPERTIES:")
    print(":RESPONSE: " + response)
    if partner:
        print(":ONE_ON_ONE_WITH: " + partner)

    if location is not None:
        print(":LOCATION: " + location)
    print(":END:")

  print("")

def nsdate_to_local_date(d):
    return datetime.datetime.strptime(str(d),'%Y-%m-%d %H:%M:%S %z').astimezone(pytz.timezone('Europe/Vienna'))

def print_org_format(events, config):
    my_email = config['Main']['my_email']
    for event in events:
        partner = get_one_on_one_partner(event, my_email)

        print_orgmode_entry(event.title(),
                            nsdate_to_local_date(event.startDate()),
                            nsdate_to_local_date(event.endDate()),
                            event.location(),
                            get_availability_string(event.availability()),
                            partner
                            )


if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))

    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(script_directory, 'config.cfg')))
    events = get_calendar_events(config)
    print_org_format(events, config)
