import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { WorklistPage } from './pages/WorklistPage'
import { ReadingPage } from './pages/ReadingPage'

/**
 * Plain client-side declarative routing only (<BrowserRouter>/<Routes>/
 * <Route>, <Link>, useNavigate/useParams) - no data loaders/actions, no
 * SSR, no RSC. react-router's known advisories are against those
 * server-rendering/data-API features and don't apply to how this app uses
 * the library.
 */
export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WorklistPage />} />
        <Route path="/studies/:studyId" element={<ReadingPage />} />
      </Routes>
    </BrowserRouter>
  )
}
