/* eslint-env node */

module.exports = {
    'presets': [
        [
            '@babel/preset-env', {
                // Somehow, this fixes an OpenLayers transform issue
                // in jest.
                // See: https://github.com/openlayers/openlayers/issues/7401#issuecomment-571695444
                targets: { node: 'current' }
            }
        ],
        '@babel/preset-react'
    ]
};
