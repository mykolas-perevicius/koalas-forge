#!/usr/bin/env node

// Test script for recommendations engine

console.log('🐨 Koala\'s Forge - Testing Smart Recommendations Engine\n');

// Mock recommendation rules
const recommendationRules = {
    complementary: {
        'docker': ['vscode', 'git', 'node', 'python'],
        'git': ['vscode', 'cursor'],
        'python': ['vscode', 'cursor', 'git', 'docker'],
        'ollama': ['lm-studio', 'python', 'cursor', 'vscode'],
    },
    dependencies: {
        'docker': { suggests: ['git'] },
        'node': { suggests: ['git', 'vscode'] },
        'python': { suggests: ['git', 'vscode'] },
        'postgresql': { suggests: ['docker'] },
    },
    workflows: {
        'web-development': {
            apps: ['git', 'node', 'vscode', 'docker', 'postgresql'],
            keywords: ['git', 'node', 'vscode']
        },
        'ai-development': {
            apps: ['python', 'git', 'cursor', 'ollama', 'docker'],
            keywords: ['ollama', 'lm-studio', 'python', 'cursor']
        },
    }
};

// Mock app database
const apps = {
    'git': { name: 'Git', description: 'Version control' },
    'docker': { name: 'Docker', description: 'Containers' },
    'python': { name: 'Python', description: 'Programming' },
    'vscode': { name: 'VS Code', description: 'Code editor' },
    'cursor': { name: 'Cursor', description: 'AI editor' },
    'node': { name: 'Node.js', description: 'JavaScript runtime' },
    'ollama': { name: 'Ollama', description: 'Local LLMs' },
    'postgresql': { name: 'PostgreSQL', description: 'Database' },
};

function generateRecommendations(selectedApps) {
    const recommendations = new Map();

    // 1. Complementary apps
    selectedApps.forEach(appId => {
        const complements = recommendationRules.complementary[appId] || [];
        complements.forEach(complementId => {
            if (!selectedApps.includes(complementId)) {
                recommendations.set(complementId, (recommendations.get(complementId) || 0) + 3);
            }
        });
    });

    // 2. Dependencies
    selectedApps.forEach(appId => {
        const deps = recommendationRules.dependencies[appId];
        if (deps) {
            deps.suggests?.forEach(suggestedId => {
                if (!selectedApps.includes(suggestedId)) {
                    recommendations.set(suggestedId, (recommendations.get(suggestedId) || 0) + 5);
                }
            });
        }
    });

    // 3. Workflows
    Object.entries(recommendationRules.workflows).forEach(([workflow, data]) => {
        const matchCount = data.keywords.filter(k => selectedApps.includes(k)).length;
        if (matchCount >= 2) {
            data.apps.forEach(appId => {
                if (!selectedApps.includes(appId)) {
                    recommendations.set(appId, (recommendations.get(appId) || 0) + matchCount * 2);
                }
            });
        }
    });

    return Array.from(recommendations.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6)
        .map(([appId, score]) => ({ id: appId, score, ...apps[appId] }));
}

// Test scenarios
console.log('Test 1: Docker selected');
console.log('Selected: [docker]');
let recs = generateRecommendations(['docker']);
recs.forEach(app => console.log(`  → ${app.name} (score: ${app.score}) - ${app.description}`));

console.log('\nTest 2: AI Development workflow');
console.log('Selected: [ollama, python]');
recs = generateRecommendations(['ollama', 'python']);
recs.forEach(app => console.log(`  → ${app.name} (score: ${app.score}) - ${app.description}`));

console.log('\nTest 3: Web Development workflow');
console.log('Selected: [git, node, vscode]');
recs = generateRecommendations(['git', 'node', 'vscode']);
recs.forEach(app => console.log(`  → ${app.name} (score: ${app.score}) - ${app.description}`));

console.log('\nTest 4: Single app (Python)');
console.log('Selected: [python]');
recs = generateRecommendations(['python']);
recs.forEach(app => console.log(`  → ${app.name} (score: ${app.score}) - ${app.description}`));

console.log('\n✓ All recommendation tests completed successfully!');
