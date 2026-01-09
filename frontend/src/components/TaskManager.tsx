import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { Task, TaskCreate, TaskStatus, TaskPriority } from '../types'

export default function TaskManager() {
  const [isCreating, setIsCreating] = useState(false)
  const [newTask, setNewTask] = useState<TaskCreate>({
    title: '',
    description: '',
    priority: TaskPriority.MEDIUM,
    estimated_pomodoros: 1,
  })
  const [filter, setFilter] = useState<TaskStatus | 'all'>('all')

  const queryClient = useQueryClient()

  // Fetch tasks
  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks', filter],
    queryFn: () =>
      api.tasks.list(filter !== 'all' ? { status: filter } : undefined),
  })

  // Create task mutation
  const createMutation = useMutation({
    mutationFn: api.tasks.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      setIsCreating(false)
      setNewTask({
        title: '',
        description: '',
        priority: TaskPriority.MEDIUM,
        estimated_pomodoros: 1,
      })
    },
  })

  // Update task mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      api.tasks.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  // Delete task mutation
  const deleteMutation = useMutation({
    mutationFn: api.tasks.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  // Complete task mutation
  const completeMutation = useMutation({
    mutationFn: api.tasks.complete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const handleCreateTask = (e: React.FormEvent) => {
    e.preventDefault()
    if (newTask.title.trim()) {
      createMutation.mutate(newTask)
    }
  }

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.URGENT:
        return 'text-red-600 bg-red-50'
      case TaskPriority.HIGH:
        return 'text-orange-600 bg-orange-50'
      case TaskPriority.MEDIUM:
        return 'text-blue-600 bg-blue-50'
      case TaskPriority.LOW:
        return 'text-gray-600 bg-gray-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.TODO:
        return 'bg-gray-100 text-gray-800'
      case TaskStatus.IN_PROGRESS:
        return 'bg-blue-100 text-blue-800'
      case TaskStatus.COMPLETED:
        return 'bg-green-100 text-green-800'
      case TaskStatus.ARCHIVED:
        return 'bg-gray-100 text-gray-600'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Tasks</h2>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="btn btn-primary"
        >
          {isCreating ? 'Cancel' : '+ New Task'}
        </button>
      </div>

      {/* Create Task Form */}
      {isCreating && (
        <form onSubmit={handleCreateTask} className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Title *</label>
              <input
                type="text"
                className="input w-full"
                value={newTask.title}
                onChange={(e) =>
                  setNewTask({ ...newTask, title: e.target.value })
                }
                placeholder="Task title"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                className="input w-full"
                value={newTask.description}
                onChange={(e) =>
                  setNewTask({ ...newTask, description: e.target.value })
                }
                placeholder="Task description (optional)"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <select
                  className="input w-full"
                  value={newTask.priority}
                  onChange={(e) =>
                    setNewTask({
                      ...newTask,
                      priority: e.target.value as TaskPriority,
                    })
                  }
                >
                  <option value={TaskPriority.LOW}>Low</option>
                  <option value={TaskPriority.MEDIUM}>Medium</option>
                  <option value={TaskPriority.HIGH}>High</option>
                  <option value={TaskPriority.URGENT}>Urgent</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Estimated Pomodoros
                </label>
                <input
                  type="number"
                  className="input w-full"
                  value={newTask.estimated_pomodoros}
                  onChange={(e) =>
                    setNewTask({
                      ...newTask,
                      estimated_pomodoros: parseInt(e.target.value) || 1,
                    })
                  }
                  min="1"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">
                Create Task
              </button>
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="btn"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Filter */}
      <div className="mb-4">
        <div className="flex gap-2 flex-wrap">
          {['all', TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED].map(
            (status) => (
              <button
                key={status}
                onClick={() => setFilter(status as TaskStatus | 'all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === status
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {status === 'all' ? 'All' : status.replace('_', ' ')}
              </button>
            )
          )}
        </div>
      </div>

      {/* Task List */}
      {isLoading && <p className="text-center text-gray-500">Loading tasks...</p>}

      {error && (
        <p className="text-center text-red-500">
          Failed to load tasks. Please try again.
        </p>
      )}

      {data && data.tasks.length === 0 && (
        <p className="text-center text-gray-500 py-8">
          No tasks found. Create your first task to get started!
        </p>
      )}

      {data && data.tasks.length > 0 && (
        <div className="space-y-3">
          {data.tasks.map((task: Task) => (
            <div
              key={task.id}
              className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-lg">{task.title}</h3>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(
                        task.priority
                      )}`}
                    >
                      {task.priority}
                    </span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                        task.status
                      )}`}
                    >
                      {task.status.replace('_', ' ')}
                    </span>
                  </div>

                  {task.description && (
                    <p className="text-gray-600 text-sm mb-2">{task.description}</p>
                  )}

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>
                      🍅 {task.completed_pomodoros}/{task.estimated_pomodoros}
                    </span>
                    <span>
                      Created {new Date(task.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2 ml-4">
                  {task.status !== TaskStatus.COMPLETED && (
                    <>
                      {task.status === TaskStatus.TODO && (
                        <button
                          onClick={() =>
                            updateMutation.mutate({
                              id: task.id,
                              data: { status: TaskStatus.IN_PROGRESS },
                            })
                          }
                          className="text-sm text-blue-600 hover:text-blue-700"
                        >
                          Start
                        </button>
                      )}
                      <button
                        onClick={() => completeMutation.mutate(task.id)}
                        className="text-sm text-green-600 hover:text-green-700"
                      >
                        Complete
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => deleteMutation.mutate(task.id)}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {data && data.total > 0 && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          Showing {data.tasks.length} of {data.total} tasks
        </div>
      )}
    </div>
  )
}
