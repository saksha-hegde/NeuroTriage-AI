import type { WindowPreset } from '../../types/study'

interface WindowPresetControlProps {
  value: WindowPreset
  onChange: (preset: WindowPreset) => void
}

const PRESETS: { value: WindowPreset; label: string }[] = [
  { value: 'brain', label: 'Brain (WW 80 / WL 40)' },
  { value: 'blood', label: 'Blood/ICH (WW 100 / WL 50)' },
  { value: 'dicom', label: 'DICOM default' },
]

/**
 * Window/level preset selector for the CT viewer. Purely a display choice -
 * switching presets just changes the image URL CTImageViewer requests
 * (see api/client.ts's sliceImageUrl); the AI overlay is a separate layer
 * positioned independently of the image's pixel content, so it's unaffected
 * by which preset is active.
 */
export function WindowPresetControl({ value, onChange }: WindowPresetControlProps) {
  return (
    <label className="flex items-center gap-2 text-sm text-clinical-text">
      Window
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as WindowPreset)}
        className="rounded border border-clinical-border bg-clinical-surface px-2 py-1 text-sm text-clinical-text"
      >
        {PRESETS.map((preset) => (
          <option key={preset.value} value={preset.value}>
            {preset.label}
          </option>
        ))}
      </select>
    </label>
  )
}
