import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ABTestMonitor } from './pages/ABTestMonitor'
import { Dashboard } from './pages/Dashboard'
import { Review } from './pages/Review'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/workflows/:id" element={<Review />} />
          <Route path="/workflows/:id/ab-test" element={<ABTestMonitor />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
