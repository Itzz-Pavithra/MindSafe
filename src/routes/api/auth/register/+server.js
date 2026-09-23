import { json } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import { User } from '$lib/server/models/User.js';
import { generateToken, setAuthCookie } from '$lib/server/auth.js';

export async function POST({ request, cookies }) {
  try {
    const { name, email, password } = await request.json();

    if (!name || !email || !password) {
      return json({ success: false, error: 'Name, email, and password are required' }, { status: 400 });
    }

    if (password.length < 6) {
      return json({ success: false, error: 'Password must be at least 6 characters' }, { status: 400 });
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
    const existingUser = await User.findOne({ email: trimmedEmail });

    if (existingUser) {
      return json({ success: false, error: 'An account with this email already exists' }, { status: 409 });
    }

    const passwordHash = await User.hashPassword(password);
    const newUser = await User.create({
      name: name.trim(),
      email: trimmedEmail,
      passwordHash,
      role: 'survey_user'
    });

    // Auto log in after registration
    const token = generateToken(newUser);
    setAuthCookie(cookies, token);

    return json({
      success: true,
      message: 'Account created successfully',
      user: {
        id: newUser._id.toString(),
        email: newUser.email,
        name: newUser.name,
        role: newUser.role
      }
    });
  } catch (error) {
    console.error('Registration error:', error);
    return json({ success: false, error: 'Failed to complete registration' }, { status: 500 });
  }
}
