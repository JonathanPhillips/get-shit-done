// Task types
export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum TaskStatus {
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

export interface Task {
  id: number
  title: string
  description?: string
  status: TaskStatus
  priority: TaskPriority
  estimated_pomodoros: number
  completed_pomodoros: number
  created_at: string
  updated_at: string
  completed_at?: string
  tags?: string
  github_issue_url?: string
}

export interface TaskCreate {
  title: string
  description?: string
  priority?: TaskPriority
  estimated_pomodoros?: number
  tags?: string
  github_issue_url?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  estimated_pomodoros?: number
  completed_pomodoros?: number
  tags?: string
  github_issue_url?: string
}

// Pomodoro types
export enum SessionType {
  WORK = 'work',
  SHORT_BREAK = 'short_break',
  LONG_BREAK = 'long_break',
}

export enum SessionStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  INTERRUPTED = 'interrupted',
}

export interface PomodoroSession {
  id: number
  session_type: SessionType
  status: SessionStatus
  planned_duration: number
  actual_duration?: number
  started_at: string
  ended_at?: string
  task_id?: number
  session_number: number
  notes?: string
  interruptions: number
}

export interface PomodoroSessionCreate {
  session_type: SessionType
  planned_duration: number
  task_id?: number
  session_number?: number
}

export interface PomodoroStats {
  total_sessions: number
  completed_sessions: number
  total_work_time: number
  total_break_time: number
  average_session_duration: number
  interruptions_count: number
  today_sessions: number
  today_work_time: number
  current_streak: number
}
