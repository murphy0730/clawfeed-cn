/**
 * Date & text formatting utilities.
 */

/**
 * Format an ISO date string to a human-friendly format.
 * @param {string} dateStr - ISO date string
 * @param {boolean} withTime - include time
 */
export function formatDate(dateStr, withTime = true) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  if (!withTime) return `${y}-${m}-${day}`;
  const h = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  return `${y}-${m}-${day} ${h}:${min}`;
}

/**
 * Relative time (e.g. "3 分钟前", "2 小时前").
 */
export function timeAgo(dateStr) {
  if (!dateStr) return "";
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diff = Math.floor((now - then) / 1000);
  if (diff < 60) return "刚刚";
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)} 天前`;
  return formatDate(dateStr, false);
}

/**
 * Truncate text to max length.
 */
export function truncate(text, max = 100) {
  if (!text || text.length <= max) return text || "";
  return text.slice(0, max) + "...";
}

/**
 * Digest type label.
 */
const TYPE_LABELS = {
  "4h": "4小时简报",
  daily: "日报",
  weekly: "周报",
  monthly: "月报",
};

export function digestTypeLabel(type) {
  return TYPE_LABELS[type] || type;
}
