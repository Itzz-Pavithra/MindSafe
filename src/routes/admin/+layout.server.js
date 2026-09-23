import { redirect } from '@sveltejs/kit';

export function load({ locals }) {
  if (!locals.user) {
    throw redirect(303, '/admin-login');
  }
  if (locals.user.role !== 'admin') {
    throw redirect(303, '/dashboard');
  }
  return {
    user: locals.user
  };
}
