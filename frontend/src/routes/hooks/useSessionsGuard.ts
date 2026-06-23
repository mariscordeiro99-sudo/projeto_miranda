export const useSessionGuard = () => {
  const SESSION_KEY = '@App:last_access';
  const TWELVE_HOURS_MS = 12 * 60 * 60 * 1000;

  const saveExitTime = () => {
    localStorage.setItem(SESSION_KEY, Date.now().toString());
  };

  const shouldRequireLogin = (): boolean => {
    const token = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('user') || localStorage.getItem('user_data');
    const lastAccess = localStorage.getItem(SESSION_KEY);

    if (!token || !storedUser) {
      return true;
    }

    if (!lastAccess) {
      return true;
    }

    const timeElapsed = Date.now() - parseInt(lastAccess, 10);
    return timeElapsed >= TWELVE_HOURS_MS;
  };

  return { saveExitTime, shouldRequireLogin };
};
