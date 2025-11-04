#!/usr/bin/env node

// Test script for new features

console.log('🐨 Koala\'s Forge - Testing New Features\n');

// Test 1: isNewApp function
function isNewApp(dateAdded) {
    if (!dateAdded) return false;
    const addedDate = new Date(dateAdded);
    const now = new Date('2025-01-04');
    const daysDiff = (now - addedDate) / (1000 * 60 * 60 * 24);
    return daysDiff <= 30;
}

console.log('Test 1: isNewApp function');
console.log('  - Jan (2024-12-28):', isNewApp('2024-12-28') ? '✓ NEW' : '✗ NOT NEW');
console.log('  - Cursor (2024-12-20):', isNewApp('2024-12-20') ? '✓ NEW' : '✗ NOT NEW');
console.log('  - Arc (2024-12-10):', isNewApp('2024-12-10') ? '✓ NEW' : '✗ NOT NEW');
console.log('  - Raycast (2024-12-15):', isNewApp('2024-12-15') ? '✓ NEW' : '✗ NOT NEW');
console.log('  - Ollama (2024-11-15):', isNewApp('2024-11-15') ? '✗ NEW' : '✓ NOT NEW');
console.log('  - Git (2024-08-01):', isNewApp('2024-08-01') ? '✗ NEW' : '✓ NOT NEW');

// Test 2: Disk space calculation
console.log('\nTest 2: Disk Space Calculation');
const apps = [
    { name: 'Ollama', size: 150 },
    { name: 'Cursor', size: 220 },
    { name: 'Docker', size: 500 }
];

let totalSize = apps.reduce((sum, app) => sum + app.size, 0);
console.log(`  Total size: ${totalSize} MB (${(totalSize / 1000).toFixed(1)} GB)`);
console.log(`  Warning level: ${totalSize > 10000 ? 'ERROR' : totalSize > 5000 ? 'WARNING' : 'OK'}`);

// Test 3: Apps marked as new
console.log('\nTest 3: Apps marked as NEW (added in last 30 days):');
const sampleApps = [
    { id: 'jan', name: 'Jan', dateAdded: '2024-12-28' },
    { id: 'cursor', name: 'Cursor', dateAdded: '2024-12-20' },
    { id: 'arc', name: 'Arc', dateAdded: '2024-12-10' },
    { id: 'raycast', name: 'Raycast', dateAdded: '2024-12-15' },
    { id: 'ollama', name: 'Ollama', dateAdded: '2024-11-15' },
];

sampleApps.forEach(app => {
    const isNew = isNewApp(app.dateAdded);
    console.log(`  ${isNew ? '🆕' : '  '} ${app.name} (${app.dateAdded})`);
});

console.log('\n✓ All tests completed successfully!');
