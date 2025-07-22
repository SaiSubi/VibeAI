import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Home from './pages/Home'
import Results from './pages/Results'
import HomeGen from './pages/HomeGen'
import ResultsGen from './pages/ResultsGen'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/home" element={<Home />} />
        <Route path="/results" element={<Results />} />
        <Route path="/homegen" element={<HomeGen />} />
        <Route path="/resultsgen" element={<ResultsGen />} />
      </Routes>
    </Router>
  )
}

export default App
