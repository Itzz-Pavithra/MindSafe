import jwt from 'jsonwebtoken';
import { env } from '$env/dynamic/private';

const getJwtSecret = () => env.JWT_SECRET || process.env.JWT_SECRET || 'mindsafe-secure-token-2026-key-academic';
const COOKIE_NAME = 'auth_token';

export function generateToken(user) {
  return jwt.sign(
    {
      id: user._id.toString(),
      email: user.email,
      name: user.name,
      role: user.role
    },
    getJwtSecret(),
    { expiresIn: '7d' }
  );
}

export function verifyToken(token) {
  try {
    return jwt.verify(token, getJwtSecret());
  } catch (error) {
    return null;
  }
}

export function setAuthCookie(cookies, token) {
  cookies.set(COOKIE_NAME, token, {
    httpOnly: true,
    path: '/',
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7 // 7 days
  });
}

export function clearAuthCookie(cookies) {
  cookies.delete(COOKIE_NAME, { path: '/' });
}

export function getUserFromCookies(cookies) {
  const token = cookies.get(COOKIE_NAME);
  if (!token) return null;
  return verifyToken(token);
}
