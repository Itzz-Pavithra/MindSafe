import { getUserFromCookies } from '$lib/server/auth.js';
import { redirect, json } from '@sveltejs/kit';

export async function handle({ event, resolve }) {
  // Extract user from secure httpOnly cookie
  const user = getUserFromCookies(event.cookies);
  event.locals.user = user;

  const pathname = event.url.pathname;

  // Protect Survey submission API & ML API
  if (pathname.startsWith('/api/survey') || pathname.startsWith('/api/ml')) {
    if (!user) {
      return json({ success: false, error: 'Authentication required' }, { status: 401 });
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
