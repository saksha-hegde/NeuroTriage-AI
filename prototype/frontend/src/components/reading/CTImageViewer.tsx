import { useEffect, useState } from 'react'
import { sliceImageUrl } from '../../api/client'
import type { OverlayRegion, WindowPreset } from '../../types/study'

interface CTImageViewerProps {
  studyId: string
  sliceCount: number
  currentIndex: number
  onIndexChange: (index: number) => void
  overlay: OverlayRegion | null
  showOverlay: boolean
  windowPreset: WindowPreset
}

/**
 * Renders the current CT slice with prev/next + a slider, and (optionally)
 * the AI's highlighted region for the slice it applies to.
 *
 * The overlay is positioned as a percentage of this container
 * (left/top/width/height from OverlayRegion, all 0-1 fractions) rather than
 * pixels, so it's correct regardless of the real image's actual
 * dimensions. This assumes the image fills its (square) container the same
 * way on both axes - true for the common CT acquisition matrix (e.g.
 * 512x512) this prototype targets; a non-square real image would need the
 * container's aspect-ratio adjusted to match. Because the overlay is a
 * separate DOM layer rather than something baked into the image pixels, it
 * stays correctly positioned no matter which window/level preset is active
 * - windowing only changes pixel intensities, never the image's geometry.
 */
export function CTImageViewer({
  studyId,
  sliceCount,
  currentIndex,
  onIndexChange,
  overlay,
  showOverlay,
  windowPreset,
}: CTImageViewerProps) {
  const [imageFailed, setImageFailed] = useState(false)

  // A new slice, or a new window/level preset, is a new image request -
  // give it a fresh chance to load.
  useEffect(() => {
    setImageFailed(false)
  }, [studyId, currentIndex, windowPreset])

  const overlayVisibleHere = showOverlay && overlay !== null && overlay.slice_index === currentIndex

  if (sliceCount <= 0) {
    return (
      <div className="flex aspect-square w-full items-center justify-center rounded-lg border border-clinical-border bg-black text-sm text-slate-400">
        No slices available for this study yet.
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-clinical-border bg-black">
        {!imageFailed ? (
          <img
            src={sliceImageUrl(studyId, currentIndex, windowPreset)}
            alt={`CT slice ${currentIndex + 1} of ${sliceCount}`}
            className="h-full w-full object-contain"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center gap-1 px-6 text-center">
            <span className="text-sm text-slate-400">CT image not available yet.</span>
            <span className="text-xs text-slate-500">
              Real anonymized slices are added via backend/app/data/README.md.
            </span>
          </div>
        )}

        {overlayVisibleHere && overlay && (
          <div
            className="pointer-events-none absolute rounded-sm border-2 border-red-500 bg-red-500/25"
            style={{
              left: `${overlay.x * 100}%`,
              top: `${overlay.y * 100}%`,
              width: `${overlay.width * 100}%`,
              height: `${overlay.height * 100}%`,
            }}
            aria-hidden="true"
          />
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => onIndexChange(Math.max(0, currentIndex - 1))}
          disabled={currentIndex === 0}
          className="rounded border border-clinical-border px-2 py-1 text-sm text-clinical-text disabled:opacity-40"
        >
          ← Prev
        </button>
        <input
          type="range"
          min={0}
          max={Math.max(0, sliceCount - 1)}
          value={currentIndex}
          onChange={(event) => onIndexChange(Number(event.target.value))}
          className="flex-1"
          aria-label="CT slice"
        />
        <button
          type="button"
          onClick={() => onIndexChange(Math.min(sliceCount - 1, currentIndex + 1))}
          disabled={currentIndex === sliceCount - 1}
          className="rounded border border-clinical-border px-2 py-1 text-sm text-clinical-text disabled:opacity-40"
        >
          Next →
        </button>
        <span className="w-16 shrink-0 text-right text-sm text-clinical-muted">
          {currentIndex + 1} / {sliceCount}
        </span>
      </div>
    </div>
  )
}
