import { getUserFromCookies } from '$lib/server/auth.js';
import { redirect, json } from '@sveltejs/kit';

export async function handle({ event, resolve }) {
  // Extract user from secure httpOnly cookie
  const user = getUserFromCookies(event.cookies);
  event.locals.user = user;

  const pathname = event.url.pathname;

  // Protect Admin API endpoints
  if (pathname.startsWith('/api/admin')) {
    if (!user) {
      return json({ success: false, error: 'Authentication required' }, { status: 401 });
    }
    if (user.role !== 'admin') {
      return json({ success: false, error: 'Access restricted to administrators' }, { status: 403 });
    }
  }

  // Protect Survey submission API & ML API
  if (pathname.startsWith('/api/survey') || pathname.startsWith('/api/ml')) {
    if (!user) {
      return json({ success: false, error: 'Authentication required' }, { status: 401 });
    }
  }

  // Protect Admin web routes
  if (pathname === '/admin' || pathname.startsWith('/admin/')) {
    if (!user) {
      throw redirect(303, '/admin-login');
    }
    if (user.role !== 'admin') {
      throw redirect(303, '/dashboard');
    }
  }

  // Protect Survey User web routes
  const protectedUserRoutes = ['/dashboard', '/assessment', '/result', '/profile'];
  if (protectedUserRoutes.some(route => pathname === route || pathname.startsWith(route + '/'))) {
    if (!user) {
      throw redirect(303, '/login');
    }
  }

  return await resolve(event);
}
