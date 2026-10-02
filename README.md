# Appointment Scanner — Android phone app — v1.1.0

Appointment Scanner turns appointment letters and lifeboat operations rosters into checked calendar entries on an Android phone.

## What changed in v1.1.0

### Lifeboat roster scanning

The scanner now automatically recognises RNLI-style **Lifeboat Operations Rota / roster** tables in addition to ordinary appointment letters.

For a recognised roster it:

1. Uses OCR layout coordinates to preserve the table columns.
2. Finds the configured person's name (default: **Sean Durcan**).
3. Extracts only the rows in which that person is rostered.
4. Identifies that person's position from the column heading.
5. Extracts the other people on the same shift and their positions.
6. Creates one editable draft calendar entry per matched roster date.
7. Runs the normal calendar clash and travel-time checks before saving each entry.
8. Keeps the original scanned/imported roster with the saved entry.

Default roster times are:

- **Tuesday: 19:30**
- **Thursday: 19:30**
- **Sunday: 09:30**

These defaults are editable in **Settings & Backup**, and every extracted date/time remains editable on the review screen before it is saved. A saved roster event can also be edited later in the same way as an ordinary appointment.

The default roster location is **Sligo Bay Lifeboat Station** and the default roster duration is 120 minutes. Both can be changed in Settings.

### Roster alerts

Roster entries request four normal Android Calendar alerts:

- 2 days before
- 1 day before
- 2 hours before
- 15 minutes before

A separate exact Android alarm is also scheduled for **10 minutes before** a roster entry using `AlarmManager.setAlarmClock()`.

### Ordinary appointments remain unchanged

Ordinary appointment letters retain their existing defaults:

- default duration: 120 minutes when no end time is supplied;
- calendar reminders: 2 days, 1 day and 2 hours before;
- separate exact alarm: 2 hours before.

## Build versions

- Android Gradle Plugin: 9.4.0
- Gradle: 9.6.0
- compileSdk / targetSdk: 37
- minimum Android: API 26 / Android 8.0
- JDK: 17 or newer

The application ID remains `com.seandurcan.appointmentscanner`, so v1.1.0 installs over the existing Appointment Scanner rather than creating a second app.
