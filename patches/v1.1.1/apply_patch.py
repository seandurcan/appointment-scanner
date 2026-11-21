from pathlib import Path
import sys

root = Path(sys.argv[1])

# Bump app version.
p = root / "app/build.gradle.kts"
s = p.read_text()
s = s.replace('versionCode = 12', 'versionCode = 13')
s = s.replace('versionName = "1.1.0"', 'versionName = "1.1.1"')
p.write_text(s)

# Allow invoking the phone Clock app's public SET_ALARM intent.
p = root / "app/src/main/AndroidManifest.xml"
s = p.read_text()
needle = '    <uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />\n'
if 'com.android.alarm.permission.SET_ALARM' not in s:
    s = s.replace(needle, needle + '    <uses-permission android:name="com.android.alarm.permission.SET_ALARM" />\n')
p.write_text(s)

# Copy the new Clock integration helper.
src = Path(__file__).with_name("ClockAlarmIntegration.kt")
dst = root / "app/src/main/java/com/seandurcan/appointmentscanner/ClockAlarmIntegration.kt"
dst.write_text(src.read_text())

# Update UI wording/version.
p = root / "app/src/main/java/com/seandurcan/appointmentscanner/Screens.kt"
s = p.read_text()
s = s.replace('Text("Version 1.1.0"', 'Text("Version 1.1.1"')
s = s.replace(
    'if (initial.alarmMinutesBefore > 0) Text("Exact alarm: ${CalendarRepository.labelReminder(initial.alarmMinutesBefore)} before")',
    '''if (initial.alarmMinutesBefore > 0) {
                    Text("Exact backup alarm: ${CalendarRepository.labelReminder(initial.alarmMinutesBefore)} before")
                    Text("After saving, the Clock app opens so you can confirm a visible alarm for the same time/date.", style = MaterialTheme.typography.bodySmall)
                }'''
)
s = s.replace(
    'Text("Normal appointments retain the exact 2-hour alarm. Roster entries use an exact 10-minute alarm.", style = MaterialTheme.typography.bodySmall)',
    'Text("Normal appointments retain the exact 2-hour backup alarm. Roster entries use an exact 10-minute backup alarm. After saving, the Clock app opens for a visible alarm confirmation.", style = MaterialTheme.typography.bodySmall)'
)
s = s.replace(
    'Text("Roster calendar alerts: 2 days, 1 day, 2 hours and 15 minutes. Exact alarm: 10 minutes before. Calendar alert sound follows the selected Calendar app notification settings.", style = MaterialTheme.typography.bodySmall)',
    'Text("Roster calendar alerts: 2 days, 1 day, 2 hours and 15 minutes. Exact backup alarm: 10 minutes before. The Clock app then opens for the visible alarm. Calendar alert sound follows the selected Calendar app notification settings.", style = MaterialTheme.typography.bodySmall)'
)
p.write_text(s)

# After the exact date-aware backup alarm is scheduled, open Clock to confirm a visible entry.
p = root / "app/src/main/java/com/seandurcan/appointmentscanner/MainActivity.kt"
s = p.read_text()
old = '''                        val alarmMessage = when (alarm) {
                            is AlarmScheduler.Result.Scheduled -> "Exact ${CalendarRepository.labelReminder(alarm.minutesBefore)} alarm scheduled."
                            AlarmScheduler.Result.NeedsExactAlarmPermission -> "Allow 'Alarms & reminders' in Settings to activate the exact ${CalendarRepository.labelReminder(draft.alarmMinutesBefore)} alarm."
                            AlarmScheduler.Result.NeedsNotificationPermission -> "Notification permission is required for the audible ${CalendarRepository.labelReminder(draft.alarmMinutesBefore)} alarm."
                            AlarmScheduler.Result.TooLate -> "The exact ${CalendarRepository.labelReminder(draft.alarmMinutesBefore)} alarm time has already passed."
                            AlarmScheduler.Result.Disabled -> "No separate exact alarm was requested."
                            null -> "The separate exact alarm was not scheduled."
                        }
'''
new = '''                        val alarmMessage = when (alarm) {
                            is AlarmScheduler.Result.Scheduled -> "Exact ${CalendarRepository.labelReminder(alarm.minutesBefore)} backup alarm scheduled."
                            AlarmScheduler.Result.NeedsExactAlarmPermission -> "Allow 'Alarms & reminders' in Settings to activate the exact ${CalendarRepository.labelReminder(draft.alarmMinutesBefore)} backup alarm."
                            AlarmScheduler.Result.NeedsNotificationPermission -> "Notification permission is required for the audible ${CalendarRepository.labelReminder(draft.alarmMinutesBefore)} backup alarm."
                            AlarmScheduler.Result.TooLate -> "The exact ${CalendarRepository.labelReminder(draft.alarmMinutesBefore)} alarm time has already passed."
                            AlarmScheduler.Result.Disabled -> "No separate exact alarm was requested."
                            null -> "The separate exact alarm was not scheduled."
                        }

                        val clockResult = if (alarm is AlarmScheduler.Result.Scheduled) {
                            ClockAlarmIntegration(this).openConfirmation(draft)
                        } else null
                        val clockMessage = when (clockResult) {
                            is ClockAlarmIntegration.Result.ConfirmationOpened ->
                                "Clock opened for a visible alarm at ${clockResult.timeText} on ${clockResult.dateText}. Check the date shown in Clock and tap Save."
                            ClockAlarmIntegration.Result.NoClockApp ->
                                "No compatible Clock app accepted the visible-alarm request; the exact Appointment Scanner backup alarm remains active."
                            ClockAlarmIntegration.Result.TooLate ->
                                "The visible Clock alarm time has already passed."
                            ClockAlarmIntegration.Result.Disabled ->
                                "No visible Clock alarm was requested."
                            null -> ""
                        }
'''
if old not in s:
    raise RuntimeError("Expected alarm block not found")
s = s.replace(old, new)
s = s.replace(
    '"Appointment saved in Upcoming Appointments. Phone calendar save failed: ${outcome.calendarError ?: "unknown calendar error"}. $alarmMessage"',
    '"Appointment saved in Upcoming Appointments. Phone calendar save failed: ${outcome.calendarError ?: "unknown calendar error"}. $alarmMessage $clockMessage".trim()'
)
s = s.replace(
    '"$reminderMessage $alarmMessage"',
    '"$reminderMessage $alarmMessage $clockMessage".trim()'
)
p.write_text(s)

# Add release note.
p = root / "README.md"
s = p.read_text()
s = s.replace("v1.1.0", "v1.1.1")
note = """
## v1.1.1 — visible Clock alarm confirmation

Appointment Scanner keeps its exact date-aware Android alarm as a backup and also opens the phone Clock app after a successful save so a visible Clock alarm can be confirmed. Android's public Clock intent carries hour/minute/label but not an arbitrary future calendar date, so the requested alarm date/time is included in the Clock label and the Clock UI remains visible for confirmation. If no compatible Clock app accepts the request, the app says so and retains the exact backup alarm instead of silently claiming a Clock alarm was created.

"""
if "## v1.1.1 — visible Clock alarm confirmation" not in s:
    pos = s.find("\n## What changed")
    s = s[:pos] + "\n" + note + s[pos:] if pos >= 0 else s + "\n" + note
p.write_text(s)
