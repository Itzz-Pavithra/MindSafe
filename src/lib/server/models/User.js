import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true
  },
  passwordHash: {
    type: String
  },
  password: {
    type: String
  },
  role: {
    type: String,
    enum: ['admin', 'survey_user'],
    default: 'survey_user'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, { strict: false });

// Compare password helper
userSchema.methods.comparePassword = async function(candidatePassword) {
  const hash = this.passwordHash || this.password || (this.get && (this.get('passwordHash') || this.get('password')));
  if (!hash) return false;
  return await bcrypt.compare(candidatePassword, hash);
};

// Static helper to hash password
userSchema.statics.hashPassword = async function(password) {
  const salt = await bcrypt.genSalt(10);
  return await bcrypt.hash(password, salt);
};

// Clear model cache in dev environments to prevent schema caching mismatch
if (mongoose.models && mongoose.models.User) {
  delete mongoose.models.User;
}

export const User = mongoose.model('User', userSchema);
