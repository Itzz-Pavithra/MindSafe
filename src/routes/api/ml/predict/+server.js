import { json } from '@sveltejs/kit';
import { mlService } from '$lib/server/services/mlService.js';

export async function POST({ locals }) {
  if (!locals.user) {
    return json({ success: false, error: 'Authentication required' }, { status: 401 });
  }

  // ML endpoint returns status per specification: zero fake predictions
  const result = await mlService.predict({});
  return json({
    success: false,
    connected: false,
    message: 'ML model not connected yet. Real model will be connected in Phase 2.',
    prediction: null
  });
}
