// Test security guards in api/ml/predict and admin/ml-analysis
import { POST } from '../src/routes/api/ml/predict/+server.js';
import { load } from '../src/routes/admin/ml-analysis/+page.server.js';

async function testSecurity() {
  console.log('--- Testing Security Guards ---');

  // 1. Unauthenticated prediction request
  const unauthRes = await POST({
    request: new Request('http://localhost/api/ml/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ assessment: { age: '18–22' } })
    }),
    locals: {} // No user
  });

  const unauthStatus = unauthRes.status;
  const unauthJson = await unauthRes.json();
  if (unauthStatus === 401 && unauthJson.error === 'Authentication required') {
    console.log('✔ Unauthenticated prediction request successfully rejected with HTTP 401.');
  } else {
    throw new Error(`Expected 401 Authentication required, got status ${unauthStatus}`);
  }

  // 2. Non-admin access to admin ML analytics
  let caughtAdminError = false;
  try {
    await load({ locals: { user: { role: 'user', name: 'Participant' } } });
  } catch (err) {
    if (err.status === 403) {
      caughtAdminError = true;
      console.log('✔ Non-admin access to admin ML analytics successfully rejected with HTTP 403.');
    } else {
      console.error('Unexpected error status:', err);
    }
  }

  if (!caughtAdminError) {
    throw new Error('Expected 403 for non-admin user on admin ML analytics');
  }

  // 3. Admin access succeeds
  const adminData = await load({ locals: { user: { role: 'admin', name: 'Administrator' } } });
  if (adminData && adminData.modelInfo && adminData.shapImportance.length > 0) {
    console.log(`✔ Authenticated admin successfully loaded ML analytics (${adminData.shapImportance.length} SHAP features).`);
  } else {
    throw new Error('Admin load failed to retrieve ML analytics');
  }

  console.log('--- All Security Guards Verified Successfully ---');
}

testSecurity().catch(err => {
  console.error('Security test failed:', err);
  process.exit(1);
});
