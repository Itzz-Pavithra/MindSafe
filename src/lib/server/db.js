import dns from 'node:dns';
import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import { env } from '$env/dynamic/private';
import { User } from './models/User.js';

// Only apply custom DNS servers on local Windows environments if not on Vercel/cloud serverless
if (process.platform === 'win32' && !process.env.VERCEL) {
  try {
    dns.setServers(['8.8.8.8', '1.1.1.1']);
  } catch (e) {
    // Fall back to system DNS
  }
}

function getMongoUri() {
  const uri = (env.MONGODB_URI || process.env.MONGODB_URI || '').trim();
  return uri;
}

/**
 * Global cache across hot reloads in development and serverless invocations in production.
 */
let cached = global.mongoose;
if (!cached) {
  cached = global.mongoose = { conn: null, promise: null };
}

export async function connectDB() {
  // If already connected, reuse existing active connection
  if (cached.conn && mongoose.connection.readyState === 1) {
    return cached.conn;
  }

  if (!cached.promise) {
    const uri = getMongoUri();
    if (!uri) {
      console.error('[MindSafe Server] MONGODB_URI is missing from server environment ($env/dynamic/private and process.env)');
      throw new Error('MONGODB_URI is not defined in server environment');
    }

    const opts = {
      bufferCommands: false,
      serverSelectionTimeoutMS: 10000,
      maxPoolSize: 5
    };

    cached.promise = mongoose.connect(uri, opts).then((m) => {
      console.log('[MindSafe Server] MongoDB connected successfully');

      // Asynchronously synchronize administrator account without blocking the response
      syncAdminAccount().catch((err) => {
        console.error('[MindSafe Server] Admin synchronization notice:', err.message);
      });

      return m;
    }).catch((err) => {
      cached.promise = null; // Reset promise so subsequent invocations can retry
      console.error('[MindSafe Server] MongoDB connection error:', err.message);
      throw err;
    });
  }

  try {
    cached.conn = await cached.promise;
    return cached.conn;
  } catch (error) {
    cached.promise = null;
    throw error;
  }
}

async function syncAdminAccount() {
  try {
    const adminEmail = (env.ADMIN_EMAIL || process.env.ADMIN_EMAIL || '').trim().toLowerCase();
    const adminPassword = (env.ADMIN_PASSWORD || process.env.ADMIN_PASSWORD || '').trim();

    if (!adminEmail || !adminPassword) {
      return;
    }

    const existing = await User.findOne({ email: adminEmail });
    if (!existing) {
      const salt = await bcrypt.genSalt(12);
      const passwordHash = await bcrypt.hash(adminPassword, salt);
      await User.create({
        email: adminEmail,
        name: 'Administrator',
        passwordHash,
        role: 'admin'
      });
      console.log('[MindSafe Server] Administrator account initialized in database');
    } else {
      const hash = existing.passwordHash || existing.password || '';
      const isMatch = hash ? await bcrypt.compare(adminPassword, hash) : false;
      if (!isMatch) {
        const salt = await bcrypt.genSalt(12);
        const passwordHash = await bcrypt.hash(adminPassword, salt);
        await User.updateOne({ _id: existing._id }, { $set: { passwordHash, role: 'admin' } });
        console.log('[MindSafe Server] Administrator password hash updated to match environment configuration');
      }
    }
  } catch (err) {
    console.error('[MindSafe Server] Admin synchronization notice:', err.message);
  }
}
