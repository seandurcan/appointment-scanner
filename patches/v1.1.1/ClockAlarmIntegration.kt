package com.seandurcan.appointmentscanner

import android.app.AlarmClock
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import java.time.ZoneId
import java.time.format.DateTimeFormatter

/**
 * Opens the user's Clock app to create a visible alarm entry.
 *
 * Android's public ACTION_SET_ALARM contract can pass hour/minute/message but cannot
 * carry an arbitrary one-off calendar date. For that reason this deliberately keeps
 * the Clock UI visible (EXTRA_SKIP_UI=false) and puts the required date/time in the
 * label. The date-aware AlarmScheduler alarm remains active as a reliable backup.
 */
class ClockAlarmIntegration(private val context: Context) {
    sealed interface Result {
        data class ConfirmationOpened(
            val triggerAtMillis: Long,
            val dateText: String,
            val timeText: String
        ) : Result
        data object NoClockApp : Result
        data object TooLate : Result
        data object Disabled : Result
    }

    private val dateFormatter = DateTimeFormatter.ofPattern("dd/MM/yyyy")
    private val timeFormatter = DateTimeFormatter.ofPattern("HH:mm")

    fun openConfirmation(draft: AppointmentDraft): Result {
        if (draft.alarmMinutesBefore <= 0) return Result.Disabled
        val appointmentDate = draft.date ?: return Result.TooLate
        val appointmentTime = draft.time ?: return Result.TooLate
        val triggerLocal = appointmentDate.atTime(appointmentTime)
            .minusMinutes(draft.alarmMinutesBefore.toLong())
        val triggerMillis = triggerLocal.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
        if (triggerMillis <= System.currentTimeMillis()) return Result.TooLate

        val dateText = triggerLocal.toLocalDate().format(dateFormatter)
        val timeText = triggerLocal.toLocalTime().format(timeFormatter)
        val label = buildString {
            append(draft.title.ifBlank { "Appointment" })
            append(" — ")
            append(dateText)
            append(" ")
            append(timeText)
            if (draft.location.isNotBlank()) {
                append(" — ")
                append(draft.location.trim())
            }
        }

        val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
            putExtra(AlarmClock.EXTRA_HOUR, triggerLocal.hour)
            putExtra(AlarmClock.EXTRA_MINUTES, triggerLocal.minute)
            putExtra(AlarmClock.EXTRA_MESSAGE, label)
            putExtra(AlarmClock.EXTRA_VIBRATE, true)
            putExtra(AlarmClock.EXTRA_SKIP_UI, false)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }

        return try {
            context.startActivity(intent)
            Result.ConfirmationOpened(triggerMillis, dateText, timeText)
        } catch (_: ActivityNotFoundException) {
            Result.NoClockApp
        } catch (_: SecurityException) {
            Result.NoClockApp
        }
    }
}
