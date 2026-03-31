import { defineConfig } from "eslint/config";
import react from "eslint-plugin-react";
import globals from "globals";
import babelParser from "@babel/eslint-parser";
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
        extends: [react.configs.flat.recommended],
        plugins: {
            react,
        },

        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node,
                ...globals.jquery,
                Backbone: true,
                _: true,
            },

            parser: babelParser,
            ecmaVersion: 6,
            sourceType: "module",

            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
            },
        },

        settings: {
            react: {
                version: "detect",
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
