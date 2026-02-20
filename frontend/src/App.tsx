import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { ErrorBoundary } from 'react-error-boundary'
import { Toaster } from 'react-hot-toast'
import { Layout } from './components/Layout'
import { ErrorFallback } from './components/ErrorFallback'
import { ABTestMonitor } from './pages/ABTestMonitor'
import { Dashboard } from './pages/Dashboard'
import { Review } from './pages/Review'

function App() {
  return (
    <BrowserRouter>
      <Toaster position="bottom-right" />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<ErrorBoundary FallbackComponent={ErrorFallback}><Dashboard /></ErrorBoundary>} />
          <Route path="/workflows/:id" element={<ErrorBoundary FallbackComponent={ErrorFallback}><Review /></ErrorBoundary>} />
          <Route path="/workflows/:id/ab-test" element={<ErrorBoundary FallbackComponent={ErrorFallback}><ABTestMonitor /></ErrorBoundary>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
