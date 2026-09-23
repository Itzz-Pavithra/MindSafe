import { json } from '@sveltejs/kit';
import { clearAuthCookie } from '$lib/server/auth.js';

export async function POST({ cookies }) {
  clearAuthCookie(cookies);
  return json({ success: true, message: 'Logged out successfully' });
}
