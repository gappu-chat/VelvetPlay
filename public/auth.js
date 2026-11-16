window.Auth = {
  getToken() { return localStorage.getItem('vp_token'); },
  setToken(t) { localStorage.setItem('vp_token', t); },
  clearToken() { localStorage.removeItem('vp_token'); localStorage.removeItem('vp_user'); },
  getUser() { try { return JSON.parse(localStorage.getItem('vp_user') || 'null'); } catch { return null; } },
  setUser(u) { localStorage.setItem('vp_user', JSON.stringify(u)); },
  
  async fetchMe() {
    const t = this.getToken();
    if (!t) return null;
    try {
      const res = await fetch('/api/auth/me', { headers: { Authorization: 'Bearer ' + t } });
      if (!res.ok) { this.clearToken(); return null; }
      const u = await res.json();
      this.setUser(u);
      return u;
    } catch (e) { return null; }
  },
  
  async authFetch(url, options = {}) {
    const t = this.getToken();
    options.headers = { ...(options.headers || {}), Authorization: 'Bearer ' + t };
    const res = await fetch(url, options);
    // Agar token expire ho chuka hai (401 error), toh auto logout
    if (res.status === 401) {
      this.clearToken();
      window.location.href = '/login.html';
      throw new Error('Session expired');
    }
    return res;
  },
  
  requireLogin() {
    if (!this.getToken()) { location.href = '/login.html'; return false; }
    return true;
  }
};
