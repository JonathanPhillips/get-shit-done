import { useState, useEffect, useRef } from 'react'
import { api } from '../services/api'
import { SessionType, PomodoroSession } from '../types'

interface PomodoroTimerProps {
  onSessionComplete?: (session: PomodoroSession) => void
}

const WORK_DURATION = 25 * 60 // 25 minutes in seconds
const SHORT_BREAK = 5 * 60 // 5 minutes
const LONG_BREAK = 15 * 60 // 15 minutes
const SESSIONS_UNTIL_LONG_BREAK = 4

export default function PomodoroTimer({ onSessionComplete }: PomodoroTimerProps) {
  const [currentSession, setCurrentSession] = useState<PomodoroSession | null>(null)
  const [timeRemaining, setTimeRemaining] = useState<number>(WORK_DURATION)
  const [isRunning, setIsRunning] = useState(false)
  const [sessionCount, setSessionCount] = useState(0)
  const intervalRef = useRef<number | null>(null)

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  // Timer countdown logic
  useEffect(() => {
    if (isRunning && timeRemaining > 0) {
      intervalRef.current = window.setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            handleSessionComplete()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isRunning, timeRemaining])

  // Load active session on mount
  useEffect(() => {
    loadActiveSession()
  }, [])

  const loadActiveSession = async () => {
    try {
      const session = await api.pomodoro.getActive()
      if (session) {
        setCurrentSession(session)
        const elapsed = Math.floor(
          (Date.now() - new Date(session.started_at).getTime()) / 1000
        )
        const remaining = Math.max(0, session.planned_duration - elapsed)
        setTimeRemaining(remaining)
        if (remaining > 0) {
          setIsRunning(true)
        }
      }
    } catch (error) {
      console.error('Failed to load active session:', error)
    }
  }

  const startSession = async (type: SessionType) => {
    try {
      const duration = type === SessionType.WORK
        ? WORK_DURATION
        : type === SessionType.SHORT_BREAK
        ? SHORT_BREAK
        : LONG_BREAK

      const session = await api.pomodoro.sessions.start({
        session_type: type,
        planned_duration: duration,
        session_number: sessionCount + 1,
      })

      setCurrentSession(session)
      setTimeRemaining(duration)
      setIsRunning(true)
    } catch (error) {
      console.error('Failed to start session:', error)
    }
  }

  const pauseSession = () => {
    setIsRunning(false)
  }

  const resumeSession = () => {
    setIsRunning(true)
  }

  const handleSessionComplete = async () => {
    if (!currentSession) return

    try {
      const completed = await api.pomodoro.sessions.complete(currentSession.id)
      setIsRunning(false)

      if (completed.session_type === SessionType.WORK) {
        setSessionCount((prev) => prev + 1)
      }

      if (onSessionComplete) {
        onSessionComplete(completed)
      }

      setCurrentSession(null)
      setTimeRemaining(WORK_DURATION)

      // Play completion sound/notification
      playNotification()
    } catch (error) {
      console.error('Failed to complete session:', error)
    }
  }

  const interruptSession = async () => {
    if (!currentSession) return

    try {
      await api.pomodoro.sessions.interrupt(currentSession.id)
      setIsRunning(false)
      setCurrentSession(null)
      setTimeRemaining(WORK_DURATION)
    } catch (error) {
      console.error('Failed to interrupt session:', error)
    }
  }

  const playNotification = () => {
    // Simple browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Pomodoro Complete!', {
        body: 'Time for a break!',
        icon: '/vite.svg',
      })
    }
  }

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getNextBreakType = (): SessionType => {
    return sessionCount % SESSIONS_UNTIL_LONG_BREAK === SESSIONS_UNTIL_LONG_BREAK - 1
      ? SessionType.LONG_BREAK
      : SessionType.SHORT_BREAK
  }

  const getSessionColor = () => {
    if (!currentSession) return 'bg-primary-600'
    switch (currentSession.session_type) {
      case SessionType.WORK:
        return 'bg-focus-work'
      case SessionType.SHORT_BREAK:
        return 'bg-focus-break'
      case SessionType.LONG_BREAK:
        return 'bg-focus-longBreak'
      default:
        return 'bg-primary-600'
    }
  }

  return (
    <div className="card">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">
          {currentSession
            ? currentSession.session_type.replace('_', ' ').toUpperCase()
            : 'POMODORO TIMER'}
        </h2>

        {/* Timer Display */}
        <div
          className={`text-7xl font-mono font-bold my-8 p-8 rounded-lg ${getSessionColor()} text-white`}
        >
          {formatTime(timeRemaining)}
        </div>

        {/* Session Counter */}
        <div className="mb-6 text-sm text-gray-600">
          <p>Sessions completed today: {sessionCount}</p>
        </div>

        {/* Controls */}
        <div className="flex gap-3 justify-center flex-wrap">
          {!currentSession ? (
            <>
              <button
                onClick={() => startSession(SessionType.WORK)}
                className="btn btn-primary"
              >
                Start Work Session
              </button>
              <button
                onClick={() => startSession(getNextBreakType())}
                className="btn"
              >
                Start Break
              </button>
            </>
          ) : (
            <>
              {isRunning ? (
                <button onClick={pauseSession} className="btn btn-primary">
                  Pause
                </button>
              ) : (
                <button onClick={resumeSession} className="btn btn-primary">
                  Resume
                </button>
              )}
              <button onClick={interruptSession} className="btn">
                Stop
              </button>
              <button onClick={handleSessionComplete} className="btn">
                Skip
              </button>
            </>
          )}
        </div>

        {/* Progress Bar */}
        {currentSession && (
          <div className="mt-6">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${getSessionColor()}`}
                style={{
                  width: `${
                    ((currentSession.planned_duration - timeRemaining) /
                      currentSession.planned_duration) *
                    100
                  }%`,
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
