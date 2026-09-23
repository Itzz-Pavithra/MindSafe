import { json } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import mongoose from 'mongoose';

export async function GET() {
  try {
    await connectDB();

    if (mongoose.connection.readyState === 1) {
      return json({
        database: 'connected'
      }, { status: 200 });
    } else {
      console.error('[Health Check] Database readyState is not 1:', mongoose.connection.readyState);
      return json({
        database: 'unavailable'
      }, { status: 503 });
    }
  } catch (error) {
    // Technical error is logged ONLY on the server console, NEVER exposed to client
    console.error('[Health Check] Database connection failure:', error.message);
    return json({
      database: 'unavailable'
    }, { status: 503 });
  }
}
