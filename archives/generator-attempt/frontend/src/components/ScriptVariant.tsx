import type { ScriptVariant as ScriptVariantType } from '../types/workflows'

interface ScriptVariantProps {
  variant: ScriptVariantType
  checked: boolean
  disabled?: boolean
  onSelect: (scriptId: string) => void
}

export function ScriptVariant({ variant, checked, disabled, onSelect }: ScriptVariantProps) {
  return (
    <label className={`panel script-card ${checked ? 'script-card-active' : ''}`}>
      <input
        type="radio"
        name="script-choice"
        value={variant.id}
        checked={checked}
        disabled={disabled}
        onChange={() => onSelect(variant.id)}
      />
      <div>
        <h3>{variant.hook}</h3>
        <p>{variant.body}</p>
        <p>
          <strong>CTA:</strong> {variant.cta}
        </p>
      </div>
    </label>
  )
}
