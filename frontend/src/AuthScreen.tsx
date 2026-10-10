import { useState, type FormEvent } from 'react'

const API_URL = 'http://localhost:8000/api'

type AuthScreenProps = {
  onAuthenticated: (token: string, email: string) => void
}

function AuthScreen({ onAuthenticated }: AuthScreenProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed. Please try again.')
      }
      onAuthenticated(data.access_token, data.user.email)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Authentication failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-content" aria-labelledby="auth-title">
        <div className="auth-brand">AURA <span>PERSONAL OPERATIONS</span></div>
        <div className="auth-heading">
          <p className="eyebrow">YOUR PRIVATE WORKSPACE</p>
          <h1 id="auth-title">{mode === 'login' ? 'Welcome back.' : 'Create your account.'}</h1>
          <p>{mode === 'login' ? 'Sign in to continue to your workspace.' : 'Start with a private workspace for your tasks and notes.'}</p>
        </div>
        <div className="auth-tabs" role="tablist" aria-label="Account access">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'login'}
            className={mode === 'login' ? 'active' : ''}
            onClick={() => { setMode('login'); setError('') }}
          >
            Sign in
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'register'}
            className={mode === 'register' ? 'active' : ''}
            onClick={() => { setMode('register'); setError('') }}
          >
            Create account
          </button>
        </div>
        <form className="auth-form" onSubmit={submit}>
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={8}
              maxLength={72}
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 8 characters"
            />
          </label>
          {error && <p className="auth-error" role="alert">{error}</p>}
          <button type="submit" disabled={submitting}>
            {submitting ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>
      </section>
      <aside className="auth-aside" aria-hidden="true">
        <div className="auth-aside-mark">A</div>
        <p>Keep your work<br />in your hands.</p>
      </aside>
    </main>
  )
}

export default AuthScreen