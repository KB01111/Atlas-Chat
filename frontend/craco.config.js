const path = require('path');

module.exports = {
  webpack: {
    alias: {
      '@components': path.resolve(__dirname, 'client/src/components'),
      '@hooks': path.resolve(__dirname, 'client/src/hooks'),
      '@providers': path.resolve(__dirname, 'client/src/Providers'),
      '@routes': path.resolve(__dirname, 'client/src/routes'),
      '@store': path.resolve(__dirname, 'client/src/store'),
      '@utils': path.resolve(__dirname, 'client/src/utils'),
      '@api': path.resolve(__dirname, 'client/src/api-client.js'),
      '@data-provider': path.resolve(__dirname, 'packages/data-provider/src'),
    },
  },
};