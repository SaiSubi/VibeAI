import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Home from './pages/Home'
import Results from './pages/Results'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/home" element={<Home />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </Router>
  )
}

export default App
