import { useEffect, useState, type FormEvent } from 'react'
import AuthScreen from './AuthScreen'

const API_URL = 'http://localhost:8000/api'

type Health = {
  status: string
  service: string
}

type MemoryItem = {
  id: number
  type: string
  content: string
}

type DocumentItem = {
  id: number
  title: string
  source?: string
  content: string
}

type DocumentSearchResult = {
  id: number
  title: string
  source?: string
  match: string
}

type TaskItem = {
  id: number
  title: string
  description?: string
  status: string
  priority: string
}

type ApprovalItem = {
  id: number
  action: string
  risk_level: number
  reason?: string
  status: string
  requires_approval: boolean
  created_at: string
}

type AgentRunResult = {
  agent: string
  summary?: string
  plan?: string[]
  status?: string
  workflow?: {
    task_manager?: {
      tasks?: string[]
    }
  }
  [key: string]: unknown
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('aura.access_token') || '')
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem('aura.email') || '')
  const [health, setHealth] = useState<Health | null>(null)
  const [request, setRequest] = useState("Prepare me for tomorrow's interview.")
  const [result, setResult] = useState<AgentRunResult | null>(null)
  const [agentError, setAgentError] = useState('')
  const [runningAgent, setRunningAgent] = useState(false)
  const [importingPlanTasks, setImportingPlanTasks] = useState(false)
  const [planTasksImported, setPlanTasksImported] = useState(false)
  const [memories, setMemories] = useState<MemoryItem[]>([])
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [memoryType, setMemoryType] = useState('semantic')
  const [memoryContent, setMemoryContent] = useState('')
  const [memoryError, setMemoryError] = useState('')
  const [savingMemory, setSavingMemory] = useState(false)
  const [documentTitle, setDocumentTitle] = useState('')
  const [documentSource, setDocumentSource] = useState('')
  const [documentContent, setDocumentContent] = useState('')
  const [documentError, setDocumentError] = useState('')
  const [savingDocument, setSavingDocument] = useState(false)
  const [documentQuery, setDocumentQuery] = useState('')
  const [documentResults, setDocumentResults] = useState<DocumentSearchResult[] | null>(null)
  const [searchingDocuments, setSearchingDocuments] = useState(false)
  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [taskTitle, setTaskTitle] = useState('')
  const [taskDescription, setTaskDescription] = useState('')
  const [taskPriority, setTaskPriority] = useState('medium')
  const [taskError, setTaskError] = useState('')
  const [savingTask, setSavingTask] = useState(false)
  const [approvals, setApprovals] = useState<ApprovalItem[]>([])
  const [approvalAction, setApprovalAction] = useState('')
  const [approvalReason, setApprovalReason] = useState('')
  const [approvalRisk, setApprovalRisk] = useState('1')
  const [approvalError, setApprovalError] = useState('')
  const [savingApproval, setSavingApproval] = useState(false)
  const [approvingId, setApprovingId] = useState<number | null>(null)

  const logout = () => {
    localStorage.removeItem('aura.access_token')
    localStorage.removeItem('aura.email')
    setToken('')
    setUserEmail('')
    setTasks([])
    setApprovals([])
    setMemories([])
    setDocuments([])
    setResult(null)
  }

  const apiFetch = (path: string, init: RequestInit = {}) => {
    const headers = new Headers(init.headers)
    headers.set('Authorization', `Bearer ${token}`)
    return fetch(`${API_URL}${path}`, { ...init, headers })
  }

  const handleAuthenticated = (accessToken: string, email: string) => {
    localStorage.setItem('aura.access_token', accessToken)
    localStorage.setItem('aura.email', email)
    setTasks([])
    setApprovals([])
    setMemories([])
    setDocuments([])
    setResult(null)
    setToken(accessToken)
    setUserEmail(email)
  }

  useEffect(() => {
    if (!token) return

    apiFetch('/health')
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth({ status: 'offline', service: 'aura-backend' }))

    apiFetch('/memory')
      .then((res) => res.json())
      .then((data) => setMemories(Array.isArray(data) ? data : []))
      .catch(() => setMemories([]))

    apiFetch('/documents')
      .then((res) => res.json())
      .then((data) => setDocuments(Array.isArray(data) ? data : []))
      .catch(() => setDocuments([]))

    apiFetch('/tasks')
      .then((res) => {
        if (!res.ok) throw new Error('Could not load tasks.')
        return res.json()
      })
      .then((data) => setTasks(Array.isArray(data) ? data : []))
      .catch(() => setTaskError('Tasks could not be loaded. Check that the backend is running.'))

    apiFetch('/approvals')
      .then((res) => {
        if (!res.ok) throw new Error('Could not load approvals.')
        return res.json()
      })
      .then((data) => setApprovals(Array.isArray(data) ? data : []))
      .catch(() => setApprovalError('Approvals could not be loaded. Check that the backend is running.'))
  }, [token])

  const createTask = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSavingTask(true)
    setTaskError('')

    try {
      const response = await apiFetch('/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: taskTitle,
          description: taskDescription || null,
          priority: taskPriority,
        }),
      })
      if (!response.ok) throw new Error('Task could not be created.')
      const task: TaskItem = await response.json()
      setTasks((current) => [task, ...current])
      setTaskTitle('')
      setTaskDescription('')
      setTaskPriority('medium')
    } catch {
      setTaskError('Task could not be created. Please try again.')
    } finally {
      setSavingTask(false)
    }
  }

  const toggleTaskStatus = async (task: TaskItem) => {
    const status = task.status === 'completed' ? 'pending' : 'completed'
    setTaskError('')
    try {
      const response = await apiFetch(`/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      })
      if (!response.ok) throw new Error('Task could not be updated.')
      const updated: TaskItem = await response.json()
      setTasks((current) => current.map((item) => item.id === updated.id ? updated : item))
    } catch {
      setTaskError('Task status could not be updated. Please try again.')
    }
  }

  const createApproval = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSavingApproval(true)
    setApprovalError('')
    try {
      const response = await apiFetch('/approvals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: approvalAction,
          reason: approvalReason || null,
          risk_level: Number(approvalRisk),
        }),
      })
      if (!response.ok) throw new Error('Approval request could not be created.')
      const approval: ApprovalItem = await response.json()
      setApprovals((current) => [approval, ...current])
      setApprovalAction('')
      setApprovalReason('')
      setApprovalRisk('1')
    } catch {
      setApprovalError('Approval request could not be created. Please try again.')
    } finally {
      setSavingApproval(false)
    }
  }

  const approveRequest = async (approval: ApprovalItem) => {
    setApprovingId(approval.id)
    setApprovalError('')
    try {
      const response = await apiFetch(`/approvals/${approval.id}/approve`, { method: 'POST' })
      if (!response.ok) throw new Error('Approval could not be updated.')
      const updated: ApprovalItem = await response.json()
      setApprovals((current) => current.map((item) => item.id === updated.id ? updated : item))
    } catch {
      setApprovalError('Request could not be approved. Please try again.')
    } finally {
      setApprovingId(null)
    }
  }

  const completedTasks = tasks.filter((task) => task.status === 'completed').length
  const pendingTasks = tasks.length - completedTasks
  const pendingApprovals = approvals.filter((approval) => approval.status === 'pending')

  const createMemory = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSavingMemory(true)
    setMemoryError('')
    try {
      const response = await apiFetch('/memory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: memoryType, content: memoryContent }),
      })
      if (!response.ok) throw new Error('Memory could not be saved.')
      const memory: MemoryItem = await response.json()
      setMemories((current) => [memory, ...current])
      setMemoryContent('')
    } catch {
      setMemoryError('Memory could not be saved. Please try again.')
    } finally {
      setSavingMemory(false)
    }
  }

  const createDocument = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSavingDocument(true)
    setDocumentError('')
    try {
      const response = await apiFetch('/documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: documentTitle,
          content: documentContent,
          source: documentSource || null,
        }),
      })
      if (!response.ok) throw new Error('Document could not be saved.')
      const document: DocumentItem = await response.json()
      setDocuments((current) => [document, ...current])
      setDocumentTitle('')
      setDocumentSource('')
      setDocumentContent('')
      setDocumentResults(null)
      setDocumentQuery('')
    } catch {
      setDocumentError('Document could not be saved. Please try again.')
    } finally {
      setSavingDocument(false)
    }
  }

  const searchDocuments = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!documentQuery.trim()) {
      setDocumentResults(null)
      setDocumentError('')
      return
    }
    setSearchingDocuments(true)
    setDocumentError('')
    try {
      const response = await apiFetch('/documents/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: documentQuery }),
      })
      if (!response.ok) throw new Error('Document search failed.')
      const data: { results: DocumentSearchResult[] } = await response.json()
      setDocumentResults(data.results)
    } catch {
      setDocumentError('Document search failed. Please try again.')
    } finally {
      setSearchingDocuments(false)
    }
  }

  const addPlanTasks = async () => {
    const proposedTasks = result?.workflow?.task_manager?.tasks ?? []
    const existingTitles = new Set(tasks.map((task) => task.title.trim().toLowerCase()))
    const newTitles = proposedTasks.filter((title) => !existingTitles.has(title.trim().toLowerCase()))
    setImportingPlanTasks(true)
    setAgentError('')
    const createdTasks: TaskItem[] = []
    try {
      for (const title of newTitles) {
        const response = await apiFetch('/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, description: 'Suggested by the Supervisor workflow.', priority: 'medium' }),
        })
        if (!response.ok) throw new Error('A suggested task could not be added.')
        createdTasks.push(await response.json())
      }
      setTasks((current) => [...createdTasks, ...current])
      setPlanTasksImported(true)
      if (newTitles.length === 0) setAgentError('All suggested tasks are already in your task list.')
    } catch {
      setTasks((current) => [...createdTasks, ...current])
      setAgentError('Some suggested tasks could not be added. You can retry the remaining tasks.')
    } finally {
      setImportingPlanTasks(false)
    }
  }

  const runAgent = async () => {
    setRunningAgent(true)
    setAgentError('')
    try {
      const response = await apiFetch('/agents/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: request }),
      })
      if (!response.ok) throw new Error('Supervisor could not run.')
      const data: AgentRunResult = await response.json()
      setResult(data)
      setPlanTasksImported(false)
    } catch {
      setAgentError('Supervisor could not run. Check the backend and try again.')
    } finally {
      setRunningAgent(false)
    }
  }

  if (!token) return <AuthScreen onAuthenticated={handleAuthenticated} />

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">AURA</div>
        <nav>
          <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>Dashboard</button>
          <button onClick={() => document.getElementById('tasks')?.scrollIntoView({ behavior: 'smooth' })}>Tasks</button>
          <button onClick={() => document.getElementById('agents')?.scrollIntoView({ behavior: 'smooth' })}>Agents</button>
          <button onClick={() => document.getElementById('memory')?.scrollIntoView({ behavior: 'smooth' })}>Memory</button>
          <button onClick={() => document.getElementById('documents')?.scrollIntoView({ behavior: 'smooth' })}>Documents</button>
          <button onClick={() => document.getElementById('approvals')?.scrollIntoView({ behavior: 'smooth' })}>Approvals</button>
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <h1>Good evening, {userEmail.split('@')[0] || 'User'}</h1>
          <div className="topbar-actions">
            <span className={`status ${health?.status === 'ok' ? 'online' : 'offline'}`}>
              {health ? health.status : 'connecting'}
            </span>
            <button className="logout-button" onClick={logout}>Sign out</button>
          </div>
        </header>

        <section className="cards">
          <div className="card">
            <span>Today's Tasks</span>
            <strong>{tasks.length}</strong>
          </div>
          <div className="card">
            <span>Completed</span>
            <strong>{completedTasks}</strong>
          </div>
          <div className="card">
            <span>Pending</span>
            <strong>{pendingTasks}</strong>
          </div>
        </section>

        <section className="panel task-panel" id="tasks">
          <div className="section-heading">
            <div>
              <p className="eyebrow">WORK QUEUE</p>
              <h2>Tasks</h2>
            </div>
            <span className="task-count">{pendingTasks} open</span>
          </div>

          <form className="task-form" onSubmit={createTask}>
            <label>
              Task title
              <input
                required
                value={taskTitle}
                onChange={(event) => setTaskTitle(event.target.value)}
                placeholder="e.g. Review interview notes"
              />
            </label>
            <label>
              Description
              <input
                value={taskDescription}
                onChange={(event) => setTaskDescription(event.target.value)}
                placeholder="Optional details"
              />
            </label>
            <label className="priority-field">
              Priority
              <select value={taskPriority} onChange={(event) => setTaskPriority(event.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
            <button type="submit" disabled={savingTask || !taskTitle.trim()}>
              {savingTask ? 'Adding…' : 'Add task'}
            </button>
          </form>

          {taskError && <p className="error-message" role="alert">{taskError}</p>}
          {tasks.length === 0 ? (
            <p className="empty-state">No tasks yet. Add one to get started.</p>
          ) : (
            <ul className="task-list">
              {tasks.map((task) => (
                <li className={`task-row ${task.status === 'completed' ? 'is-complete' : ''}`} key={task.id}>
                  <button
                    className="task-check"
                    type="button"
                    aria-label={task.status === 'completed' ? `Reopen ${task.title}` : `Complete ${task.title}`}
                    onClick={() => toggleTaskStatus(task)}
                  >
                    {task.status === 'completed' ? '✓' : ''}
                  </button>
                  <div className="task-copy">
                    <strong>{task.title}</strong>
                    {task.description && <span>{task.description}</span>}
                  </div>
                  <span className={`priority priority-${task.priority}`}>{task.priority}</span>
                  <span className="task-status">{task.status.replace('_', ' ')}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="panel approval-panel" id="approvals">
          <div className="section-heading">
            <div>
              <p className="eyebrow">REVIEW QUEUE</p>
              <h2>Approvals</h2>
            </div>
            <span className="task-count">{pendingApprovals.length} pending</span>
          </div>

          <form className="approval-form" onSubmit={createApproval}>
            <label>
              Action
              <input
                required
                value={approvalAction}
                onChange={(event) => setApprovalAction(event.target.value)}
                placeholder="e.g. Submit application"
              />
            </label>
            <label>
              Reason
              <input
                value={approvalReason}
                onChange={(event) => setApprovalReason(event.target.value)}
                placeholder="What will this action do?"
              />
            </label>
            <label className="risk-field">
              Risk
              <select value={approvalRisk} onChange={(event) => setApprovalRisk(event.target.value)}>
                <option value="1">Low</option>
                <option value="2">Medium</option>
                <option value="3">High</option>
              </select>
            </label>
            <button type="submit" disabled={savingApproval || !approvalAction.trim()}>
              {savingApproval ? 'Submitting…' : 'Request review'}
            </button>
          </form>

          {approvalError && <p className="error-message" role="alert">{approvalError}</p>}
          {approvals.length === 0 ? (
            <p className="empty-state">No approval requests yet.</p>
          ) : (
            <ul className="approval-list">
              {approvals.map((approval) => (
                <li className="approval-row" key={approval.id}>
                  <div className="approval-copy">
                    <strong>{approval.action.replace(/_/g, ' ')}</strong>
                    {approval.reason && <span>{approval.reason}</span>}
                    <small>Risk {approval.risk_level} · {new Date(approval.created_at).toLocaleDateString()}</small>
                  </div>
                  <span className={`approval-status status-${approval.status}`}>{approval.status}</span>
                  {approval.status === 'pending' ? (
                    <button
                      className="approve-button"
                      type="button"
                      disabled={approvingId === approval.id}
                      onClick={() => approveRequest(approval)}
                    >
                      {approvingId === approval.id ? 'Approving…' : 'Approve'}
                    </button>
                  ) : <span className="approval-done">Reviewed</span>}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="panel" id="agents">
          <h2>Supervisor Prompt</h2>
          <textarea
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            rows={4}
          />
          <button onClick={runAgent} disabled={runningAgent || !request.trim()}>
            {runningAgent ? 'Running…' : 'Run Supervisor'}
          </button>
          {agentError && <p className="error-message" role="alert">{agentError}</p>}
        </section>

        <section className="panel">
          <h2>Execution Output</h2>
          <pre>{result ? JSON.stringify(result, null, 2) : 'No output yet.'}</pre>
          {result?.workflow?.task_manager?.tasks?.length ? (
            <button
              className="plan-import-button"
              type="button"
              disabled={importingPlanTasks || planTasksImported}
              onClick={addPlanTasks}
            >
              {importingPlanTasks ? 'Adding tasks…' : planTasksImported ? 'Tasks added' : `Add ${result.workflow.task_manager.tasks.length} suggested tasks`}
            </button>
          ) : null}
        </section>

        <section className="info-grid">
          <div className="panel resource-panel" id="memory">
            <h2>Memory</h2>
            <form className="resource-form" onSubmit={createMemory}>
              <label>
                Type
                <select value={memoryType} onChange={(event) => setMemoryType(event.target.value)}>
                  <option value="semantic">Semantic</option>
                  <option value="preference">Preference</option>
                  <option value="episodic">Episodic</option>
                </select>
              </label>
              <label>
                Memory
                <textarea required rows={3} value={memoryContent} onChange={(event) => setMemoryContent(event.target.value)} placeholder="A detail worth remembering" />
              </label>
              <button type="submit" disabled={savingMemory || !memoryContent.trim()}>
                {savingMemory ? 'Saving…' : 'Save memory'}
              </button>
            </form>
            {memoryError && <p className="error-message" role="alert">{memoryError}</p>}
            {memories.length === 0 ? <p className="empty-state">No memory items yet.</p> : (
              <ul className="resource-list">
                {memories.map((item) => (
                  <li key={item.id}><span className="resource-tag">{item.type}</span><span>{item.content}</span></li>
                ))}
              </ul>
            )}
          </div>

          <div className="panel resource-panel" id="documents">
            <h2>Documents</h2>
            <form className="resource-form document-form" onSubmit={createDocument}>
              <label>
                Title
                <input required value={documentTitle} onChange={(event) => setDocumentTitle(event.target.value)} placeholder="Document title" />
              </label>
              <label>
                Source
                <input value={documentSource} onChange={(event) => setDocumentSource(event.target.value)} placeholder="Optional filename or URL" />
              </label>
              <label>
                Content
                <textarea required rows={4} value={documentContent} onChange={(event) => setDocumentContent(event.target.value)} placeholder="Paste text to index for keyword search" />
              </label>
              <button type="submit" disabled={savingDocument || !documentTitle.trim() || !documentContent.trim()}>
                {savingDocument ? 'Saving…' : 'Add document'}
              </button>
            </form>
            <form className="document-search" onSubmit={searchDocuments}>
              <label className="sr-only" htmlFor="document-query">Search documents</label>
              <input id="document-query" value={documentQuery} onChange={(event) => setDocumentQuery(event.target.value)} placeholder="Search document text" />
              <button type="submit" disabled={searchingDocuments}>
                {searchingDocuments ? 'Searching…' : 'Search'}
              </button>
              {documentResults !== null && (
                <button type="button" className="secondary-button" onClick={() => { setDocumentResults(null); setDocumentQuery('') }}>
                  Clear
                </button>
              )}
            </form>
            {documentError && <p className="error-message" role="alert">{documentError}</p>}
            {documentResults !== null ? (
              documentResults.length === 0 ? <p className="empty-state">No matching documents.</p> : (
                <ul className="resource-list">
                  {documentResults.map((doc) => (
                    <li key={doc.id}><span>{doc.title}</span><span className="resource-meta">{doc.source || 'No source'} · {doc.match}</span></li>
                  ))}
                </ul>
              )
            ) : documents.length === 0 ? <p className="empty-state">No documents indexed yet.</p> : (
              <ul className="resource-list">
                {documents.map((doc) => (
                  <li key={doc.id}><span>{doc.title}</span><span className="resource-meta">{doc.source || 'No source'}</span></li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
