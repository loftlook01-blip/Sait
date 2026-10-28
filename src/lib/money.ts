/**
 * Делит сумму на части по долям с округлением до step так,
 * чтобы сумма частей в точности совпадала с округлённым итогом.
 */
export function splitExact(total: number, shares: number[], step = 100): { total: number; parts: number[] } {
  const rounded = Math.round(total / step) * step;
  const parts = shares.map((s) => Math.round((rounded * s) / step) * step);
  // Остаток от округления отдаём самой крупной части — так он почти незаметен
  const diff = rounded - parts.reduce((a, b) => a + b, 0);
  const max = parts.indexOf(Math.max(...parts));
  parts[max] += diff;
  return { total: rounded, parts };
}
