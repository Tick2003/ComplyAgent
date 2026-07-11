import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import ObligationExplorer from './pages/ObligationExplorer';
import ObligationDetail from './pages/ObligationDetail';
import ReviewPanel from './pages/ReviewPanel';
import ChangeFeed from './pages/ChangeFeed';
import GapAnalysis from './pages/GapAnalysis';
import IngestCircular from './pages/IngestCircular';
import QueryChat from './pages/QueryChat';
import SupervisionMode from './pages/SupervisionMode';
import ImpactDashboard from './pages/ImpactDashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="obligations" element={<ObligationExplorer />} />
          <Route path="obligations/:id" element={<ObligationDetail />} />
          <Route path="review" element={<ReviewPanel />} />
          <Route path="changes" element={<ChangeFeed />} />
          <Route path="gaps" element={<GapAnalysis />} />
          <Route path="ingest" element={<IngestCircular />} />
          <Route path="chat" element={<QueryChat />} />
          <Route path="impact" element={<ImpactDashboard />} />
          <Route path="supervisor" element={<SupervisionMode />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
