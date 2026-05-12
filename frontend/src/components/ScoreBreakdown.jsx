import React from 'react';

const ScoreBreakdown = ({ breakdown }) => {
  const categories = [
    { key: 'mission_alignment', label: 'Mission Alignment', max: 30 },
    { key: 'location', label: 'Location', max: 20 },
    { key: 'budget', label: 'Budget', max: 20 },
    { key: 'focus_areas', label: 'Focus Areas', max: 30 },
  ];

  return (
    <div className="score-breakdown">
      {categories.map((cat) => {
        const score = breakdown[cat.key] || 0;
        const percent = (score / cat.max) * 100;
        
        return (
          <div key={cat.key} className="breakdown-row">
            <div className="row-info">
              <span className="cat-label">{cat.label}</span>
              <span className="cat-score">{score}/{cat.max}</span>
            </div>
            <div className="progress-container">
              <div 
                className="progress-fill" 
                style={{ width: `${percent}%` }}
              ></div>
            </div>
          </div>
        );
      })}

      <style jsx>{`
        .score-breakdown {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .breakdown-row {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .row-info {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
        }

        .cat-label {
          color: var(--text-secondary);
        }

        .cat-score {
          font-weight: 600;
        }

        .progress-container {
          height: 4px;
          background: var(--bg-tertiary);
          border-radius: 2px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: var(--score-high);
          border-radius: 2px;
        }
      `}</style>
    </div>
  );
};

export default ScoreBreakdown;
