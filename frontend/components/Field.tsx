"use client";

interface FieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
}

export function Field({ label, value, onChange, type = "text", required }: FieldProps) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-parchment/80">{label}</span>
      <input
        type={type}
        value={value}
        required={required}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded border border-gold-dim/40 bg-ink px-3 py-2 text-parchment focus:border-gold focus:outline-none"
      />
    </label>
  );
}
