from engine.google_calendar import get_upcoming_events

def main():
    events = get_upcoming_events()
    if not events:
        print("No upcoming events found.")
    else:
        print("Upcoming events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']}")

if __name__ == "__main__":
    main()

