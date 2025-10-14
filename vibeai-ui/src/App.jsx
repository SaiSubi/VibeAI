import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Home from './pages/Home'
import Results from './pages/Results'
import HomeGen from './pages/HomeGen'
import ResultsGen from './pages/ResultsGen'
import Personal from './pages/personal'
import AdvancedSearch from './pages/AdvancedSearch'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Personal />} />
        <Route path="/landing" element={<Landing />} />
        <Route path="/home" element={<Home />} />
        <Route path="/results" element={<Results />} />
        <Route path="/homegen" element={<HomeGen />} />
        <Route path="/resultsgen" element={<ResultsGen />} />
        <Route path="/advanced-search" element={<AdvancedSearch />} />
      </Routes>
    </Router>
  )
}

export default App
