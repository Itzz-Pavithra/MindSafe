import { redirect } from '@sveltejs/kit';

export function load({ locals }) {
  if (locals.user && locals.user.role === 'admin') {
    throw redirect(303, '/admin');
  }
  return {};
}
