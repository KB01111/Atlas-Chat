module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:import/typescript',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
    project: './tsconfig.json',
    tsconfigRootDir: __dirname,
  },
  plugins: ['react', '@typescript-eslint', 'jsx-a11y', 'import', 'react-hooks'],
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: './tsconfig.json',
        // Explicitly add baseUrl and paths here, mirroring tsconfig.json
        // Note: These paths are relative to the tsconfigRootDir (frontend/client)
        // baseUrl: './src', // <---- Adding this explicitly
        // paths: {          // <---- Adding this explicitly
        //   '~/*': ['./src/*'],
        //   '~components/*': ['./src/components/*'],
        //   '~features/*': ['./src/features/*'],
        //   '~shared/*': ['./src/shared/*'],
        //   '~shared/hooks/*': ['./src/shared/hooks/*'],
        //   '~shared/utils/*': ['./src/shared/utils/*'],
        //   '~shared/Providers/*': ['./src/shared/Providers/*'],
        //   '~shared/store/*': ['./src/shared/store/*'],
        //   '~shared/data-provider/*': ['./src/shared/data-provider/*'],
        //   '~shared/common/*': ['./src/shared/common/*'],
        // },
      },
      node: true,
    },
  },
  rules: {
    'react/react-in-jsx-scope': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^' }],
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    'jsx-a11y/anchor-is-valid': 'warn',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-empty-function': 'warn',
    'jsx-a11y/click-events-have-key-events': 'warn',
    'jsx-a11y/no-static-element-interactions': 'warn',
    'import/no-unresolved': 'error',
    'import/order': [
      'warn',
      {
        groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index', 'object', 'type'],
        'newlines-between': 'always',
        alphabetize: { order: 'asc', caseInsensitive: true },
      },
    ],
    'import/newline-after-import': 'warn',
    // Turned off prop-types for TS/TSX files by default
    'react/prop-types': 'off',
  },
  overrides: [
    {
      // Enable Jest environment for test files
      files: ['*.test.{js,jsx,ts,tsx}'],
      env: {
        jest: true,
      },
      rules: {
        // Allow test files to use dev dependencies
        'import/no-extraneous-dependencies': 'off',
        // specific test file rules can go here if needed
      },
    },
    {
      // Enable prop-types for JS/JSX files specifically
      files: ['*.jsx'],
      rules: {
        'react/prop-types': 'warn', // Use 'warn' or 'error' as preferred
        '@typescript-eslint/no-var-requires': 'off', // Allow require in JSX files if needed
      },
    },
    {
      // Allow JS files (like configs) to use require
      files: ['*.js'],
      rules: {
        '@typescript-eslint/no-var-requires': 'off',
      },
    },
    // Add override for index.js if it should be ignored or treated differently
    {
      files: ['src/index.js'], // Target the specific file causing issues
      parserOptions: {
        project: null, // Indicate it's not part of the main TS project
      },
      rules: {
        'import/no-unresolved': 'off', // Turn off specific rules if needed for this file
        '@typescript-eslint/no-var-requires': 'off',
        'no-undef': 'off', // Example: Turn off undefined variable checks if it uses globals differently
      },
    },
    // Add override for SupabaseProvider.jsx if it should be ignored or treated differently
    {
      files: ['src/shared/Providers/SupabaseProvider.jsx'], // Target the specific file causing issues
      parserOptions: {
        project: null, // Indicate it's not part of the main TS project
      },
      rules: {
        'import/no-unresolved': 'off', // Turn off specific rules if needed for this file
        '@typescript-eslint/no-var-requires': 'off',
        'no-undef': 'off', // Example: Turn off undefined variable checks if it uses globals differently
        'react/prop-types': 'off',
      },
    },
  ],
  ignorePatterns: ['node_modules/', 'dist/', 'build/', '*.config.js', '*.config.ts'],
};
