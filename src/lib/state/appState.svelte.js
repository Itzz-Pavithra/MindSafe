class AppState {
  // Session State
  user = $state(null);
  role = $state(null); // 'admin' | 'survey_user' | null
  isLoggedIn = $state(false);
  isLoadingAuth = $state(true);

  // Toasts
  toasts = $state([]);

  // Initialize session from server
  async init(serverUser = null) {
    if (serverUser) {
      this.setUser(serverUser);
      this.isLoadingAuth = false;
      return;
    }

    try {
      const res = await fetch('/api/auth/me');
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.user) {
          this.setUser(data.user);
        } else {
          this.clearUser();
        }
      } else {
        this.clearUser();
      }
    } catch (e) {
      console.error('Failed to initialize session:', e);
      this.clearUser();
    } finally {
      this.isLoadingAuth = false;
    }
  }

  setUser(userData) {
    this.user = {
      id: userData.id,
      email: userData.email,
      name: userData.name || (userData.email ? userData.email.split('@')[0] : 'User'),
      roleLabel: 'Survey Respondent'
    };
    this.role = userData.role || 'survey_user';
    this.isLoggedIn = true;
  }

  clearUser() {
    this.user = null;
    this.role = null;
    this.isLoggedIn = false;
  }

  async logout() {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) {
      console.error('Logout error:', e);
    }
    this.clearUser();
    this.addToast('info', 'Signed Out', 'You have been successfully signed out.');
    window.location.href = '/login';
  }

  addToast(type, title, message) {
    const id = Math.random().toString(36).substring(2, 9);
    this.toasts = [...this.toasts, { id, type, title, message }];
    setTimeout(() => {
      this.removeToast(id);
    }, 4500);
  }

  removeToast(id) {
    this.toasts = this.toasts.filter(t => t.id !== id);
  }
}

export const appState = new AppState();
