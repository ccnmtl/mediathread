/* eslint-env node */

module.exports = {
    'setupFiles': [
        '<rootDir>/media/js/polyfills.js'
    ],
    'testMatch': [
        '<rootDir>/media/js/src/**/?(*.)(spec|test).js?(x)'
    ],
    'testEnvironment': 'jsdom',
    'transform': {
        '^.+\\.jsx?$': 'babel-jest'
    },
    moduleDirectories: [
        'node_modules'
    ],
    moduleNameMapper: {
        '^react-pdf.*$': 'react-pdf/dist/umd/entry.jest'
    },
    'transformIgnorePatterns': [
        // OpenLayers is distributed with es6 and needs to be
        // transformed with babel.
        //
        // See: https://github.com/openlayers/openlayers/issues/7401
        //
        '/node_modules/(?!ol/)'
    ]
};
