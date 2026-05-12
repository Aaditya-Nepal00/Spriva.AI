import { useState } from 'react'

function OrgProfile({ onSubmit }) {
  const [mode, setMode] = useState('manual') // 'manual' or 'auto'
  const [pastedText, setPastedText] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    mission: '',
    focus_areas: '',
    location: '',
    budget: ''
  })

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleExtract = async () => {
    if (!pastedText.trim()) return
    
    setLoading(true)
    setMessage('Agent is reading your document...')
    
    try {
      const response = await fetch('/api/intake/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: pastedText, filename: 'pasted_document' })
      })
      
      const data = await response.json()
      
      if (data.status === 'success') {
        setFormData({
          name: data.org_name || '',
          mission: data.mission || '',
          focus_areas: data.focus_areas || '',
          location: data.location || '',
          budget: data.budget_range || ''
        })
        setMessage('Profile extracted! Review and click Find Grants.')
        setMode('manual')
      } else {
        setMessage('Failed to extract profile. Please try manual entry.')
      }
    } catch (error) {
      console.error('Extraction error:', error)
      setMessage('Error connecting to Spriva Agent.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="card" style={{ maxWidth: '600px', margin: '40px auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 className="header-gradient" style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Spriva AI</h1>
        <p style={{ color: '#a1a1aa', fontSize: '1.1rem' }}>
          Find funding your nonprofit actually qualifies for
        </p>
      </div>

      {/* Mode Toggle */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
        <button 
          onClick={() => setMode('manual')}
          style={{ 
            flex: 1, 
            background: mode === 'manual' ? 'var(--accent-color)' : 'transparent',
            color: mode === 'manual' ? 'black' : 'white',
            border: mode === 'manual' ? 'none' : '1px solid var(--border-color)',
            padding: '10px'
          }}
        >
          Manual Entry
        </button>
        <button 
          onClick={() => setMode('auto')}
          style={{ 
            flex: 1, 
            background: mode === 'auto' ? 'var(--accent-color)' : 'transparent',
            color: mode === 'auto' ? 'black' : 'white',
            border: mode === 'auto' ? 'none' : '1px solid var(--border-color)',
            padding: '10px'
          }}
        >
          Auto-fill from Document
        </button>
      </div>

      {message && (
        <div style={{ 
          padding: '12px', 
          borderRadius: '8px', 
          background: 'rgba(74, 222, 128, 0.1)', 
          color: 'var(--accent-color)',
          fontSize: '0.9rem',
          marginBottom: '20px',
          border: '1px solid rgba(74, 222, 128, 0.2)'
        }}>
          {message}
        </div>
      )}

      {mode === 'auto' ? (
        <div className="auto-fill-view">
          <div className="form-group">
            <label>Paste Document Content</label>
            <textarea 
              rows="12" 
              value={pastedText} 
              onChange={(e) => setPastedText(e.target.value)}
              placeholder="Paste your annual report, past grant application, or any organization document here..."
              style={{ background: '#0a0a0a' }}
            />
          </div>
          <button 
            onClick={handleExtract}
            disabled={loading || !pastedText.trim()}
            style={{ width: '100%', height: '50px' }}
          >
            {loading ? 'Agent is analyzing...' : 'Extract Profile'}
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Organization Name</label>
            <input 
              type="text" 
              name="name" 
              value={formData.name} 
              onChange={handleChange} 
              placeholder="e.g. Nepal Education Fund" 
              required 
            />
          </div>

          <div className="form-group">
            <label>Mission Statement</label>
            <textarea 
              name="mission" 
              rows="3" 
              value={formData.mission} 
              onChange={handleChange} 
              placeholder="What is your organization's primary goal?" 
              required 
            />
          </div>

          <div className="form-group">
            <label>Focus Areas</label>
            <input 
              type="text" 
              name="focus_areas" 
              value={formData.focus_areas} 
              onChange={handleChange} 
              placeholder="Education, Health, Rural Development" 
              required 
            />
          </div>

          <div className="form-group">
            <label>Location</label>
            <input 
              type="text" 
              name="location" 
              value={formData.location} 
              onChange={handleChange} 
              placeholder="e.g. Nepal" 
              required 
            />
          </div>

          <div className="form-group">
            <label>Annual Budget</label>
            <input 
              type="text" 
              name="budget" 
              value={formData.budget} 
              onChange={handleChange} 
              placeholder="$50,000" 
              required 
            />
          </div>

          <button type="submit" style={{ width: '100%', marginTop: '10px', height: '50px' }}>
            Find Grants
          </button>
        </form>
      )}
    </div>
  )
}

export default OrgProfile
