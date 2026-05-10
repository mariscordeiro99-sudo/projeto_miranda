export const useSessionGuard = () => {
  const SESSION_KEY = '@App:last_access';
  const TWELVE_HOURS_MS = 12 * 60 * 60 * 1000;

  const saveExitTime = () => {
    localStorage.setItem(SESSION_KEY, Date.now().toString());
  };

  const shouldRequireLogin = () => {
    const lastAccess = localStorage.getItem(SESSION_KEY);
    if (!lastAccess) return true;

    const timeElapsed = Date.now() - parseInt(lastAccess);
    return timeElapsed >= TWELVE_HOURS_MS;
  };

  return { saveExitTime, shouldRequireLogin };
};