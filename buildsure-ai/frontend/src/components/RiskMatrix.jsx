const PROBABILITY = ['Almost certain', 'Likely', 'Possible', 'Unlikely', 'Rare']
const IMPACT = ['Negligible', 'Minor', 'Moderate', 'Major', 'Catastrophic']

// grid[row][col] where row 0 = probability 5, col 0 = impact 1
function cellTone(probabilityIndex, impactIndex) {
  const exposure = (5 - probabilityIndex) * (impactIndex + 1)
  if (exposure >= 17) return 'bg-hazard/85 text-site-900'
  if (exposure >= 11) return 'bg-caution/80 text-site-900'
  if (exposure >= 6) return 'bg-hivis/75 text-site-900'
  return 'bg-clear/70 text-site-900'
}

export default function RiskMatrix({ grid, title, note }) {
  if (!grid?.length) return null
  return (
    <div>
      <h3 className="font-display text-base text-concrete">{title}</h3>
      {note && <p className="mb-2 text-xs text-steel">{note}</p>}
      <div className="mt-2 flex gap-2">
        <div className="flex flex-col justify-around pr-1 text-[10px] text-steel">
          {PROBABILITY.map((p) => (
            <span key={p} className="h-9 leading-9 text-right">{p}</span>
          ))}
        </div>
        <div className="flex-1">
          <div className="grid grid-cols-5 gap-1">
            {grid.map((row, r) =>
              row.map((count, c) => (
                <div
                  key={`${r}-${c}`}
                  className={`flex h-9 items-center justify-center text-sm font-semibold ${count ? cellTone(r, c) : 'bg-site-600 text-steel/50'}`}
                  title={`${PROBABILITY[r]} × ${IMPACT[c]}: ${count} hazard(s)`}
                >
                  {count || ''}
                </div>
              )),
            )}
          </div>
          <div className="mt-1 grid grid-cols-5 gap-1 text-[10px] text-steel">
            {IMPACT.map((i) => (
              <span key={i} className="text-center">{i}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
