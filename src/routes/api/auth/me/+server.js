import { json } from '@sveltejs/kit';

export async function GET({ locals }) {
  if (!locals.user) {
    return json({ success: false, user: null });
  }

  return json({
    success: true,
    user: locals.user
  });
}
