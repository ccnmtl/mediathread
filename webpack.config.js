const path = require('path');

module.exports = (env, argv) => {
    const mode = argv.mode ||
        (process.env.WEBPACK_SERVE ? 'development' : 'production');

    return {
        entry: './media/js/src/main.jsx',
        mode: mode,
        output: {
            path: path.resolve(__dirname, 'media/js'),
            filename: 'bundle.js'
        },
        resolve: {
            extensions: ['*', '.js', '.jsx']
        },
        module: {
            rules: [
                {
                    test: /\.(js|jsx)$/,
                    include: path.resolve(__dirname, 'media/js/src'),
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            // Babel 8's preset-react enables the dev JSX
                            // transform (jsxDEV) whenever Babel's env is
                            // "development", which is the default when
                            // NODE_ENV is unset. Production React doesn't
                            // export jsxDEV, so keep Babel's env in sync
                            // with webpack's mode.
                            envName: mode,
                            presets: [
                                '@babel/preset-env', '@babel/preset-react'
                            ]
                        }
                    }
                }
            ]
        }
    };
};
