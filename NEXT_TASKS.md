# Next Tasks - Get Shit Done

Priority-ordered list of tasks to work on when continuing development.

## Immediate Tasks (Low-Hanging Fruit)

### 1. Fix Task Manager E2E Tests 🔧
**Priority**: Low (tests fail, but functionality works)
**Estimated Time**: 1-2 hours
**Complexity**: Low

**Current Status**: 5/13 tests passing (38%)

**Issue**: Component selector mismatches between test expectations and actual UI
- Tests looking for `getByLabel('Priority')` but form might use different label
- Some buttons use text-based selectors that match multiple elements
- Need to align test selectors with actual component implementation

**Files to Check**:
- `e2e-tests/tests/tasks.spec.ts` - Test file with failures
- `frontend/src/components/TaskManager.tsx` - Actual component implementation

**Approach**:
1. Read `TaskManager.tsx` to understand actual form labels and button text
2. Update test selectors to match exact component structure
3. Consider adding `data-testid` attributes for more reliable selection
4. Run tests iteratively: `npx playwright test tests/tasks.spec.ts --project=chromium`

**Success Criteria**: All 13 Task Manager tests passing

---

### 2. Validate Integration Tests ✅
**Priority**: Medium (functionality untested)
**Estimated Time**: 30 minutes
**Complexity**: Low

**Current Status**: 11 tests created but not run

**Action Items**:
```bash
cd e2e-tests
npx playwright test tests/integration.spec.ts --project=chromium
```

**If Tests Fail**:
- Check for same selector issues as Task Manager tests
- Verify cross-component interactions work (timer + tasks)
- Fix any timing issues (may need `waitForLoadState`)

**Success Criteria**: All 11 integration tests passing

---

### 3. Add Backend Test Coverage (Optional) 📊
**Priority**: Low (already at 95%)
**Estimated Time**: 1-2 hours
**Complexity**: Low-Medium

**Areas to Cover**:
1. **Error Edge Cases**:
   - Invalid session IDs
   - Malformed request payloads
   - Database connection failures

2. **Concurrent Operations**:
   - Multiple users creating sessions simultaneously
   - Race conditions on task updates

3. **Business Logic Edge Cases**:
   - Task with 0 estimated pomodoros
   - Negative duration values
   - Session started in past

**Files**:
- `backend/tests/test_tasks_api.py`
- `backend/tests/test_pomodoro_api.py`

**Success Criteria**: 100% API endpoint coverage

---

## Phase 2: Integrations (Next Major Features)

### 1. GitHub OAuth Integration 🔐
**Priority**: High (foundation for other GitHub features)
**Estimated Time**: 4-6 hours
**Complexity**: Medium

**Requirements**:
- GitHub OAuth App registration
- OAuth flow implementation (login + callback)
- Token storage in database
- User session management

**Implementation Steps**:

**Backend** (`backend/src/api/auth.py`):
```python
@router.get("/auth/github/login")
async def github_login():
    # Redirect to GitHub OAuth
    pass

@router.get("/auth/github/callback")
async def github_callback(code: str):
    # Exchange code for token
    # Store in database
    # Create user session
    pass
```

**Database Model** (`backend/src/models/user.py`):
```python
class User(Base):
    id: int
    github_id: str
    github_username: str
    github_access_token: str (encrypted)
    created_at: datetime
```

**Frontend** (`frontend/src/components/Login.tsx`):
- Login with GitHub button
- Handle OAuth callback
- Store JWT token

**Testing**:
- Mock GitHub OAuth responses
- Test token refresh logic
- Test session expiration

**Success Criteria**:
- Users can log in with GitHub
- Sessions persist across browser refreshes
- Tokens stored securely

---

### 2. Obsidian File Watcher 📝
**Priority**: Medium (high user value)
**Estimated Time**: 6-8 hours
**Complexity**: High

**Requirements**:
- File watcher for Obsidian vault directory
- Markdown parser for TODO syntax
- Bidirectional sync (Obsidian ↔ Database)
- Conflict resolution

**Implementation Steps**:

**Backend** (`backend/src/services/obsidian_watcher.py`):
```python
class ObsidianWatcher:
    async def start_watching(vault_path: str):
        # Watch for file changes
        pass

    async def parse_markdown_todos(file_content: str):
        # Extract TODO items
        pass

    async def sync_to_database(todos: list):
        # Create/update tasks
        pass
```

**Markdown Parsing**:
- Support `- [ ]` and `- [x]` syntax
- Extract task metadata (priority, tags)
- Handle nested lists
- Detect due dates

**Sync Strategy**:
- Last-write-wins for conflicts
- Track sync timestamps
- Queue changes during offline periods

**Testing**:
- Unit tests for markdown parsing
- Integration tests for file watching
- E2E tests for sync workflow

**Success Criteria**:
- TODOs in Obsidian appear in app
- Tasks created in app appear in Obsidian
- Changes sync within 5 seconds

---

### 3. GitHub Activity Tracking 📊
**Priority**: Medium (nice to have)
**Estimated Time**: 4-6 hours
**Complexity**: Medium

**Requirements**:
- Fetch user's recent commits
- Fetch open/closed PRs
- Fetch assigned issues
- Display in dashboard

**Implementation Steps**:

**Backend** (`backend/src/services/github.py`):
```python
class GitHubService:
    async def fetch_commits(user_token: str, since: datetime):
        # GitHub API call
        pass

    async def fetch_pull_requests(user_token: str):
        pass

    async def fetch_issues(user_token: str):
        pass
```

**Database Models**:
```python
class GitHubCommit(Base):
    id: int
    user_id: int
    sha: str
    message: str
    timestamp: datetime
    repo: str
```

**Frontend** (`frontend/src/components/GitHubActivity.tsx`):
- Activity feed widget
- Link to GitHub for details
- Filter by repo/date

**Success Criteria**:
- Recent activity displays on dashboard
- Updates every 15 minutes
- Links to GitHub work correctly

---

## Phase 3: Claude Intelligence (Future)

### 1. Claude API Integration 🤖
**Priority**: High (core differentiator)
**Estimated Time**: 8-12 hours
**Complexity**: High

**Features**:
- Analyze productivity patterns
- Generate daily planning prompts
- Provide focus suggestions
- Session retrospectives

**Implementation**:
- Backend service for Claude API calls
- Prompt engineering for context
- Response caching for efficiency
- Rate limiting and cost management

---

### 2. Session Analyzer 📈
**Priority**: Medium
**Estimated Time**: 4-6 hours
**Complexity**: Medium

**Features**:
- Analyze work session patterns
- Identify productive times of day
- Suggest optimal Pomodoro duration
- Track focus trends

---

### 3. Daily Planning Prompts 📅
**Priority**: Medium
**Estimated Time**: 4-6 hours
**Complexity**: Medium

**Features**:
- Morning planning prompt
- Review incomplete tasks
- Suggest priorities
- Set daily goals

---

## Phase 4: Analytics & Polish (Future)

### 1. Advanced Dashboard 📊
- Historical trends charts
- Productivity heatmap
- Goal tracking
- Weekly/monthly reports

### 2. Real-Time Updates 🔄
- WebSocket implementation
- Live session updates across devices
- Collaborative features (future)

### 3. Mobile Improvements 📱
- PWA support
- Offline mode
- Push notifications
- Mobile-specific UI

---

## Quick Reference

**Current Test Status**:
- Backend: ✅ 29/29 (100%)
- E2E Pomodoro: ✅ 10/10 (100%)
- E2E Tasks: 🔄 5/13 (38%)
- E2E Integration: 📋 11 not run

**Start Here** (on corporate machine):
```bash
# 1. Clone repo
git clone https://github.com/JonathanPhillips/get-shit-done.git
cd get-shit-done

# 2. Verify deployment
kubectl get pods -n focus-agent
curl http://192.168.0.18:30100/api/health/detailed

# 3. Fix Task Manager tests
cd e2e-tests
npx playwright test tests/tasks.spec.ts --project=chromium --reporter=line

# 4. Read component to understand selectors
code ../frontend/src/components/TaskManager.tsx
```

---

**Last Updated**: 2026-01-09
**Next Review**: After completing immediate tasks
