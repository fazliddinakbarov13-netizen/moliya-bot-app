import React, { Component, StrictMode } from 'react'
import type { ErrorInfo } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

class ErrorBoundary extends Component<{ children: React.ReactNode }, { hasError: boolean, error: Error | null, info: ErrorInfo | null }> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null, info: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught an error", error, info);
    this.setState({ info });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b', height: '100vh', fontFamily: 'monospace' }}>
          <h1 style={{ fontSize: 24, fontWeight: 'bold' }}>Nimadir xato ketdi! (React Crash)</h1>
          <p style={{ marginTop: 10 }}>Dasturlardagi xato:</p>
          <pre style={{ background: '#fef2f2', padding: 15, borderRadius: 8, marginTop: 10, whiteSpace: 'pre-wrap' }}>
            {this.state.error?.toString()}
          </pre>
          <details style={{ marginTop: 20 }}>
            <summary>Component Stack trace</summary>
            <pre style={{ fontSize: 12 }}>{this.state.info?.componentStack}</pre>
          </details>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
