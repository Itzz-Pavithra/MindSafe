import dns from 'node:dns';
dns.setServers(['8.8.8.8', '1.1.1.1']);

import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';

const uri = process.env.MONGODB_URI;
const email = (process.env.ADMIN_EMAIL || 'pavithra.workss@gmail.com').trim().toLowerCase();
const password = process.env.ADMIN_PASSWORD || 'Pavi@2209';

async function main() {
  await mongoose.connect(uri);
  const salt = await bcrypt.genSalt(12);
  const hash = await bcrypt.hash(password, salt);

  const res = await mongoose.connection.db.collection('users').updateOne(
    { email },
    { $set: { passwordHash: hash, role: 'admin', name: 'Administrator' } },
    { upsert: true }
  );
  console.log('Update result:', res);

  const doc = await mongoose.connection.db.collection('users').findOne({ email });
  const check = await bcrypt.compare(password, doc.passwordHash);
  console.log('Password comparison check for', email, ':', check);
  await mongoose.disconnect();
}

main().catch(console.error);
