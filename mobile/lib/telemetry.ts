import { authStorage } from './authStorage';

export async function logEvent(name: string, data?: any) {
  try {
    console.log(`[telemetry] ${name}`, data ?? '');
  } catch (e) {
    // swallow
  }
}

export async function handleRateLimit(key: string, retryAfterSeconds?: number) {
  try {
    const now = Date.now();
    const ttl = (retryAfterSeconds && Number.isFinite(retryAfterSeconds)) ? retryAfterSeconds * 1000 : 60 * 1000;
    const until = now + ttl;
    await authStorage.setItemAsync(`${key}_rate_limited_until`, String(until));

    const counterKey = `${key}_429_count`;
    const prev = await authStorage.getItemAsync(counterKey);
    const prevNum = prev ? parseInt(prev, 10) || 0 : 0;
    await authStorage.setItemAsync(counterKey, String(prevNum + 1));

    console.warn(`[telemetry] rate limit for ${key} until ${new Date(until).toISOString()}`);
  } catch (e) {
    console.warn('telemetry.handleRateLimit failed', e);
  }
}

export async function getRateLimitUntil(key: string) {
  const v = await authStorage.getItemAsync(`${key}_rate_limited_until`);
  return v ? Number(v) : null;
}
