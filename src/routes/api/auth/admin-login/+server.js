import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import { connectDB } from '$lib/server/db.js';
import { User } from '$lib/server/models/User.js';
import { generateToken, setAuthCookie } from '$lib/server/auth.js';

export async function POST({ request, cookies }) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return json({ success: false, error: 'Administrator email and password are required' }, { status: 400 });
    }

    try {
      await connectDB();
    } catch (dbErr) {
      return json({ 
        success: false, 
        error: 'Database connection unavailable. Please verify MongoDB service.' 
      }, { status: 503 });
    }

    const trimmedEmail = email.trim().toLowerCase();

    // 1. Check if user exists in MongoDB with role 'admin'
    let adminUser = await User.findOne({ email: trimmedEmail, role: 'admin' });

    // 2. If not found or fallback check against server environment
    const envAdminEmail = (env.ADMIN_EMAIL || process.env.ADMIN_EMAIL || '').trim().toLowerCase();
    const envAdminPassword = env.ADMIN_PASSWORD || process.env.ADMIN_PASSWORD;

    if (!adminUser && envAdminEmail && trimmedEmail === envAdminEmail && password === envAdminPassword) {
      // Create admin user in database if it matched environment credentials
      const passwordHash = await User.hashPassword(envAdminPassword);
      adminUser = await User.create({
        email: envAdminEmail,
        name: 'Administrator',
        passwordHash,
        role: 'admin'
      });
    }

    if (!adminUser) {
      return json({ success: false, error: 'Invalid administrative credentials' }, { status: 401 });
    }

    // Verify password if user was found from database
    const isMatch = await adminUser.comparePassword(password);
    if (!isMatch && !(envAdminPassword && password === envAdminPassword)) {
      return json({ success: false, error: 'Invalid administrative credentials' }, { status: 401 });
    }

    // Generate secure session token and set httpOnly cookie for persistent session
    const token = generateToken(adminUser);
    setAuthCookie(cookies, token);

    return json({
      success: true,
      message: 'Admin authentication successful',
      user: {
        id: adminUser._id.toString(),
        email: adminUser.email,
        name: adminUser.name,
        role: 'admin'
      }
    });
  } catch (error) {
    console.error('Admin authentication error:', error);
    return json({ success: false, error: 'Internal server error during administrative authentication' }, { status: 500 });
  }
}
