interface OverlayToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
}

export function OverlayToggle({ checked, onChange, disabled = false }: OverlayToggleProps) {
  return (
    <label
      className={`flex items-center gap-2 text-sm ${disabled ? 'text-clinical-muted opacity-50' : 'text-clinical-text'}`}
    >
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
        className="h-4 w-4 rounded border-clinical-border"
      />
      AI Overlay
      {disabled && <span className="text-xs">(no region highlighted for this study)</span>}
    </label>
  )
}
