/**
 * Format a date string to locale format
 * @param {string|Date} date
 * @param {object} opts - Intl.DateTimeFormat options
 * @returns {string}
 */
export function formatDate(date, opts = {}) {
  if (!date) return '';
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    ...opts,
  }).format(new Date(date));
}

/**
 * Format a relative time (e.g., "2 hours ago")
 * @param {string|Date} date
 * @returns {string}
 */
export function formatRelativeTime(date) {
  if (!date) return '';
  const now = new Date();
  const d = new Date(date);
  const diff = Math.floor((now - d) / 1000);

  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return formatDate(date);
}

/**
 * Format currency
 * @param {number} amount
 * @param {string} currency
 * @returns {string}
 */
export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format a score (0-100) as percentage
 * @param {number} score
 * @returns {string}
 */
export function formatScore(score) {
  if (score == null) return '—';
  return `${Math.round(score)}%`;
}

/**
 * Format number with compact notation
 * @param {number} num
 * @returns {string}
 */
export function formatCompact(num) {
  return new Intl.NumberFormat('en-US', { notation: 'compact' }).format(num);
}
