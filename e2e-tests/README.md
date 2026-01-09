# End-to-End Tests

Playwright-based E2E tests for Focus Agent web UI.

## Running Tests

### Using Playwright MCP Server

The tests can be run using Claude Code's Playwright MCP integration:

```bash
# Run all E2E tests
npm test

# Run specific test file
npx playwright test pomodoro.spec.ts

# Run tests in headed mode (with browser visible)
npx playwright test --headed

# Run tests in debug mode
npx playwright test --debug
```

### Test Coverage

- **Pomodoro Timer**: Session start/pause/stop, timer countdown, session transitions
- **Task Manager**: Create/update/delete tasks, task filtering, status changes
- **Integration**: Task-linked Pomodoro sessions, stats updates

## Test Structure

```
e2e-tests/
├── tests/
│   ├── pomodoro.spec.ts     # Pomodoro timer tests
│   ├── tasks.spec.ts        # Task manager tests
│   └── integration.spec.ts  # Integration tests
├── playwright.config.ts     # Playwright configuration
└── package.json             # Dependencies
```

## Configuration

Tests are configured to run against:
- **Development**: http://localhost:3000
- **k3s**: http://192.168.0.18:30100

Edit `playwright.config.ts` to change the base URL.
