import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import PomodoroTimer from '../components/PomodoroTimer'
import TaskManager from '../components/TaskManager'

export function Home() {
  const { data: healthData, isLoading } = useQuery({
    queryKey: ['health-detailed'],
    queryFn: api.health.detailed,
  })

  const { data: statsData } = useQuery({
    queryKey: ['pomodoro-stats'],
    queryFn: api.pomodoro.stats,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Focus Agent
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Your intelligent work focus assistant with Pomodoro timer and task management
        </p>
      </div>

      {/* Stats Cards */}
      {statsData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Today's Sessions</h3>
            <p className="text-3xl font-bold text-primary-600">
              {statsData.today_sessions}
            </p>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Work Time Today</h3>
            <p className="text-3xl font-bold text-primary-600">
              {Math.floor(statsData.today_work_time / 60)} min
            </p>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Total Sessions</h3>
            <p className="text-3xl font-bold text-primary-600">
              {statsData.total_sessions}
            </p>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Current Streak</h3>
            <p className="text-3xl font-bold text-primary-600">
              {statsData.current_streak} days
            </p>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Pomodoro Timer */}
        <div>
          <PomodoroTimer />
        </div>

        {/* Coming Soon Features */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-2">Coming Soon</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p>📊 Phase 2: GitHub Activity & Obsidian Sync</p>
              <p>🤖 Phase 3: Claude AI Integration</p>
              <p>📈 Phase 4: Analytics Dashboard</p>
            </div>
          </div>
        </div>
      </div>

      {/* Task Manager */}
      <div>
        <TaskManager />
      </div>

      {/* Health Status */}
      {!isLoading && healthData && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-medium">Service</span>
              <span className="text-gray-600">{healthData.service}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Version</span>
              <span className="text-gray-600">{healthData.version}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Environment</span>
              <span className="text-gray-600">{healthData.environment}</span>
            </div>

            {/* Health Checks */}
            {healthData.checks && (
              <div className="mt-4 pt-4 border-t">
                <h3 className="font-semibold mb-3">Component Health</h3>
                <div className="space-y-2">
                  {Object.entries(healthData.checks).map(([key, check]: [string, any]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="capitalize">{key}</span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          check.status === 'up'
                            ? 'bg-green-100 text-green-800'
                            : check.status === 'disabled'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {check.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Quick Start</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button className="btn-primary" disabled>
            Start Pomodoro Session
          </button>
          <button className="btn-primary" disabled>
            Create New Task
          </button>
          <button className="btn-secondary" disabled>
            View GitHub Activity
          </button>
          <button className="btn-secondary" disabled>
            Sync Obsidian Notes
          </button>
        </div>
        <p className="text-sm text-gray-500 mt-4 text-center">
          Features coming in Phase 2 & 3
        </p>
      </div>
    </div>
  )
}
