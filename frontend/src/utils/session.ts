/**
 * Generate a UUID v4
 */
export function generateSessionId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Get or create session ID from localStorage
 */
export function getSessionId(): string {
  const stored = localStorage.getItem('trello-ai-session-id');
  if (stored) {
    return stored;
  }

  const newSessionId = generateSessionId();
  localStorage.setItem('trello-ai-session-id', newSessionId);
  return newSessionId;
}

/**
 * Clear current session and generate new one
 */
export function resetSession(): string {
  const newSessionId = generateSessionId();
  localStorage.setItem('trello-ai-session-id', newSessionId);
  return newSessionId;
}
