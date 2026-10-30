
import { useState } from 'react'
import './App.css'

function App() {
  const [search, setSearch] = useState('')

  return (
    <div>
      <h1>PokeIndex</h1>
      <p>Search for Pokemon trading cards</p>

      <input
        type="text"
        placeholder="Search for a Pokemon card..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <button>Search</button>
    </div>
  )
}

export default App
