import { Routes, Route } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Home } from './pages/Home'
import { api } from './services/api'

function App() {
  // Health check query
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.health.check,
    refetchInterval: 30000, // Check every 30 seconds
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-primary-600">
                Focus Agent
              </h1>
              {health && (
                <span className="text-sm text-gray-500">
                  v{health.version} • {health.environment}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              {health && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">Connected</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          {/* Future routes */}
          {/* <Route path="/pomodoro" element={<Pomodoro />} /> */}
          {/* <Route path="/tasks" element={<Tasks />} /> */}
          {/* <Route path="/dashboard" element={<Dashboard />} /> */}
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Focus Agent - Built for productivity
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
