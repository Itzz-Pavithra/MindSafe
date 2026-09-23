import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import bcrypt from 'bcryptjs';
import { connectDB } from '$lib/server/db.js';
import { User } from '$lib/server/models/User.js';
import { generateToken, setAuthCookie } from '$lib/server/auth.js';

export async function POST({ request, cookies }) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return json({ success: false, error: 'Email and password are required' }, { status: 400 });
    }

    try {
      await connectDB();
    } catch (dbErr) {
      console.error('Database connection error in login:', dbErr);
      return json({ 
        success: false, 
        error: 'Database connection unavailable. Please verify MongoDB service.' 
      }, { status: 503 });
    }

    const trimmedEmail = email.trim().toLowerCase();
    const user = await User.findOne({ email: trimmedEmail });

    if (!user) {
      return json({ success: false, error: 'Invalid email or password' }, { status: 401 });
    }

    // Resilient password hash lookup (checks passwordHash, password, and raw document)
    const hash = user.passwordHash || user.password || (user.get && (user.get('passwordHash') || user.get('password'))) || (user._doc && (user._doc.passwordHash || user._doc.password));

    if (!hash) {
      return json({ success: false, error: 'Invalid email or password' }, { status: 401 });
    }

    let isMatch = hash ? await bcrypt.compare(password, hash) : false;

    // Fallback sync for admin account if credentials match environment
    const envAdminEmail = (env.ADMIN_EMAIL || process.env.ADMIN_EMAIL || '').trim().toLowerCase();
    const envAdminPassword = env.ADMIN_PASSWORD || process.env.ADMIN_PASSWORD;

    if (!isMatch && envAdminEmail && trimmedEmail === envAdminEmail && envAdminPassword && password === envAdminPassword) {
      const salt = await bcrypt.genSalt(12);
      const newHash = await bcrypt.hash(envAdminPassword, salt);
      await User.updateOne({ _id: user._id }, { $set: { passwordHash: newHash, role: 'admin' } });
      isMatch = true;
    }

    if (!isMatch) {
      return json({ success: false, error: 'Invalid email or password' }, { status: 401 });
    }

    // Set secure session cookie
    const token = generateToken(user);
    setAuthCookie(cookies, token);

    return json({
      success: true,
      message: 'Login successful',
      user: {
        id: user._id.toString(),
        email: user.email,
        name: user.name,
        role: user.role
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    return json({ success: false, error: 'Authentication failed. Please try again.' }, { status: 500 });
  }
}
