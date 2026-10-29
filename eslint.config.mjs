import { defineConfig } from 'eslint/config';
import eslintReact from '@eslint-react/eslint-plugin';
import eslintJs from '@eslint/js';
import globals from 'globals';
import pluginCypress from 'eslint-plugin-cypress';

export default defineConfig([
    {
        files: ['cypress/**/*.js'],
        extends: [pluginCypress.configs.recommended],
        rules: {
            'cypress/no-unnecessary-waiting': 'off',
        },
    },
    {
        files: ['**/*.{js,jsx}'],
        extends: [
            eslintJs.configs.recommended,
            eslintReact.configs['recommended'],
        ],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',

            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
            },

            globals: {
                ...globals.browser,
                ...globals.node,
                ...globals.jquery,
                Backbone: 'readonly',
                _: 'readonly',
            },
        },

        settings: {
            react: {
                version: "19.3",
            },
        },

        rules: {
            indent: ["error", 4],
            "linebreak-style": ["error", "unix"],

            "no-unused-vars": ["error", {
                vars: "all",
                args: "none",
            }],

            quotes: ["error", "single"],
            semi: ["error", "always"],

            "max-len": [2, {
                code: 80,
                tabWidth: 4,
                ignoreUrls: true,
            }],

            "space-before-function-paren": ["error", "never"],
            "space-in-parens": ["error", "never"],
            "no-trailing-spaces": ["error"],

            "key-spacing": ["error", {
                beforeColon: false,
            }],

            "func-call-spacing": ["error", "never"],
        },
    }, {
        files: ["**/*.{test,spec}.{js,jsx}"],
        languageOptions: {
            globals: {
                ...globals.jest,
            },
        },
    }
]);
