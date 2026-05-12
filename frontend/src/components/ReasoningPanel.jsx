function ReasoningPanel({ reasoning, onViewDetails, onViewAll, fullView = false }) {
  if (!reasoning) return null

  const { best_fit, reasoning: ai_logic } = reasoning

  if (!ai_logic) return null

  return (
    <div className={`card ${fullView ? '' : 'reasoning-collapsed'}`} style={{
      borderColor: '#4ade80',
      background: 'rgba(74, 222, 128, 0.03)',
      marginBottom: '40px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, fontSize: '1.5rem', display: 'flex', alignItems: 'center' }}>
          <span style={{ marginRight: '10px' }}>🤖</span> Agent Analysis
        </h2>
        <span className={`badge ${ai_logic.estimated_success_rate === 'High' ? 'badge-green' : 'badge-yellow'}`}>
          {ai_logic.estimated_success_rate} Success Chance
        </span>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <p style={{ color: '#4ade80', fontWeight: '800', fontSize: '0.8rem', textTransform: 'uppercase', marginBottom: '8px' }}>
          Best Fit Recommendation
        </p>
        <h3 style={{ marginBottom: '12px' }}>{best_fit}</h3>
        <p style={{ color: '#a1a1aa', lineHeight: '1.6' }}>
          {ai_logic.best_fit_reason}
        </p>
      </div>

      {!fullView && (
        <div style={{ display: 'flex', gap: '15px' }}>
          <button onClick={() => onViewDetails(ai_logic.best_fit_grant_id)}>
            Draft Application
          </button>
          <button onClick={onViewAll} style={{ background: '#222', color: 'white' }}>
            View Detailed Analysis
          </button>
        </div>
      )}

      {fullView && (
        <div style={{ marginTop: '40px', borderTop: '1px solid #222', paddingTop: '30px' }}>
          <h3 style={{ marginBottom: '20px' }}>Ranked Analysis</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {ai_logic.ranked_grants.map((rank) => (
              <div key={rank.grant_id} style={{
                background: '#1a1a1a',
                padding: '20px',
                borderRadius: '8px',
                borderLeft: rank.rank === 1 ? '4px solid #4ade80' : 'none'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span style={{ fontWeight: '700' }}>#{rank.rank} {rank.title}</span>
                  <span style={{ color: '#4ade80', fontWeight: '600' }}>{rank.confidence_score}% Confidence</span>
                </div>
                <p style={{ fontSize: '0.9rem', color: '#a1a1aa', marginBottom: '10px' }}>
                  <strong>Why it fits:</strong> {rank.why_good_fit}
                </p>
                <p style={{ fontSize: '0.9rem', color: '#f87171', marginBottom: '10px' }}>
                  <strong>Red Flags:</strong> {rank.red_flags}
                </p>
                <p style={{ fontSize: '0.9rem', color: '#4ade80' }}>
                  <strong>Strategy:</strong> {rank.emphasis_tip}
                </p>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '40px' }}>
            <h3 style={{ marginBottom: '15px' }}>Overall Recommendation</h3>
            <p style={{ color: '#a1a1aa', lineHeight: '1.6' }}>{ai_logic.overall_recommendation}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReasoningPanel
