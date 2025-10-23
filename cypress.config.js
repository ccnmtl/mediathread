/* eslint-env node */

const { defineConfig } = require('cypress');
const { execSync } = require('child_process');

module.exports = defineConfig({
    blockHosts: [
        '*googletagmanager.com',
        '*google-analytics.com',
        '*doubleclick.net',
    ],
    defaultCommandTimeout: 30000,
    pageLoadTimeout: 60000,
    video: false,
    waitForAnimations: false,
    e2e: {
        // We've imported your old cypress plugins here.
        // You may want to clean this up later by importing these.
        setupNodeEvents(on, config) {
            // Run the Django command before Cypress tests start
            on('before:run', () => {
                console.log('Creating Django test user instructor_one...');
                try {
                    execSync('python manage.py create_test_user', {
                        stdio: 'inherit'
                    });
                } catch (err) {
                    console.error('Failed to create test user:', err);
                }
            });

            return require('./cypress/plugins/index.js')(on, config);
        },
        baseUrl: 'http://localhost:8000',
    },
});
