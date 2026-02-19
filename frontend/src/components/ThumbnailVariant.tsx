import type { ThumbnailVariant as ThumbnailVariantType } from '../types/workflows'

interface ThumbnailVariantProps {
  variant: ThumbnailVariantType
  checked: boolean
  disabled?: boolean
  onSelect: (thumbnailId: string) => void
}

const styleLabels: Record<string, string> = {
  'face_focus': 'Face Focus',
  'product_demo': 'Product Demo',
  'viral': 'Viral',
}

export function ThumbnailVariant({ variant, checked, disabled, onSelect }: ThumbnailVariantProps) {
  return (
    <label className={`panel thumbnail-card ${checked ? 'thumbnail-card-active' : ''}`}>
      <input
        type="radio"
        name="thumbnail-choice"
        value={variant.id}
        checked={checked}
        disabled={disabled}
        onChange={() => onSelect(variant.id)}
      />
      <div className="thumbnail-wrapper">
        <div className="thumbnail-image-container">
          <img
            src={variant.image_url}
            alt={`Thumbnail ${variant.id}`}
            loading="lazy"
            className="thumbnail-image"
            crossOrigin="anonymous"
          />
          <span className="thumbnail-style-label">{styleLabels[variant.style] || variant.style}</span>
          <span className="thumbnail-watermark">Pollinations AI</span>
        </div>
      </div>
    </label>
  )
}
