import { AppRouter, PageTitle } from './components'
import { BrowserRouter } from 'react-router-dom'
import './styles'

const App: React.FC = () => {
  return (
    <BrowserRouter basename='/sports_win_rate_analyze'>
      <PageTitle />
      <AppRouter />
    </BrowserRouter>
  )
}

export default App
