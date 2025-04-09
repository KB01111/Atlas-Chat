const path = require('path');


module.exports = {
  webpack: {
    alias: {
      '~': path.resolve(__dirname, 'client/src'),
      '~components': path.resolve(__dirname, 'client/src/components'),
      '~features': path.resolve(__dirname, 'client/src/features'),
      '~shared': path.resolve(__dirname, 'client/src/shared'),
      '~shared/hooks': path.resolve(__dirname, 'client/src/shared/hooks'),
      '~shared/utils': path.resolve(__dirname, 'client/src/shared/utils'),
      '~shared/Providers': path.resolve(__dirname, 'client/src/shared/Providers'),
      '~shared/store': path.resolve(__dirname, 'client/src/shared/store'),
      '~shared/data-provider': path.resolve(__dirname, 'client/src/shared/data-provider'),
      '~shared/common': path.resolve(__dirname, 'client/src/shared/common')
    },
  },
};