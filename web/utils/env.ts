export const isTruthyEnv = (value: string | undefined, defaultValue = false): boolean => {
  if (value === undefined || value.trim() === '')
    return defaultValue

  const normalized = value.trim().toLowerCase()
  return normalized === 'true' || normalized === '1' || normalized === 'yes' || normalized === 'y'
}
