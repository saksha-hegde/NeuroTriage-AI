import { AppRouter } from './router'

function App() {
  return (
    <div className="min-h-screen bg-clinical-bg text-clinical-text">
      <header className="border-b border-clinical-border bg-clinical-surface px-6 py-4">
        <h1 className="text-lg font-semibold">NeuroTriage AI — Prototype</h1>
        <p className="text-sm text-clinical-muted">
          Simulated Data — Not for Clinical Use
        </p>
      </header>

      <main>
        <AppRouter />
      </main>
    </div>
  )
}

export default App
