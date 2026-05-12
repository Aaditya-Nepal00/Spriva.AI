function GrantList({ grants, onSelectGrant }) {
  const getBadgeClass = (score) => {
    if (score >= 70) return 'badge-green'
    if (score >= 50) return 'badge-yellow'
    return 'badge-red'
  }

  return (
    <div className="grant-list" style={{ marginTop: '40px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0 }}>All Matching Grants</h3>
        <span style={{ color: '#a1a1aa', fontSize: '0.9rem' }}>Found {grants.length} grants</span>
      </div>

      <div className="grid">
        {grants.map((grant, index) => (
          <div key={grant.id || index} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            {index === 0 && <div className="best-match-banner">Best Match</div>}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', lineHeight: '1.3' }}>{grant.title}</h4>
              <span className={`badge ${getBadgeClass(grant.eligibility_score || 0)}`}>
                {grant.eligibility_score || 0}% Match
              </span>
            </div>

            <p style={{ color: '#a1a1aa', fontSize: '0.9rem', margin: '0 0 15px 0' }}>{grant.funder}</p>

            <div style={{ flex: 1 }}>
              <p style={{ fontSize: '0.85rem', color: '#888', fontStyle: 'italic', margin: '0 0 20px 0' }}>
                "Why this fits: {grant.reasoning_snippet || 'Mission alignment with focus on local community impact.'}"
              </p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto' }}>
              <span style={{ fontWeight: '600', color: '#4ade80' }}>{grant.amount_text || grant.amount || 'Flexible'}</span>
              <button
                onClick={() => onSelectGrant(grant)}
                style={{ padding: '6px 12px', fontSize: '0.8rem', background: '#222', color: 'white' }}
              >
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default GrantList
