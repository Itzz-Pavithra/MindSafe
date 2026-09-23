import { json } from '@sveltejs/kit';
import { mlService } from '$lib/server/services/mlService.js';

export async function GET() {
  const status = await mlService.getStatus();
  return json({
    success: true,
    ...status
  });
}
