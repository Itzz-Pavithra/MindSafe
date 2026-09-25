import { redirect } from '@sveltejs/kit';

export function load({ locals }) {
  if (locals.user) {
    if (locals.user.role === 'admin') {
      throw redirect(303, '/admin');
    }
    throw redirect(303, '/dashboard');
  }
  return {};
}
