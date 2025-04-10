module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '^~/(.*)$': '<rootDir>/src/$1',
    '^~components/(.*)$': '<rootDir>/src/components/$1',
    '^~features/(.*)$': '<rootDir>/src/features/$1',
    '^~shared/(.*)$': '<rootDir>/src/shared/$1',
    '^~shared/hooks/(.*)$': '<rootDir>/src/shared/hooks/$1',
    '^~shared/utils/(.*)$': '<rootDir>/src/shared/utils/$1',
    '^~shared/Providers/(.*)$': '<rootDir>/src/shared/Providers/$1',
    '^~shared/store/(.*)$': '<rootDir>/src/shared/store/$1',
    '^~shared/data-provider/(.*)$': '<rootDir>/src/shared/data-provider/$1',
    '^~shared/common/(.*)$': '<rootDir>/src/shared/common/$1',
  },
  setupFilesAfterEnv: ['@testing-library/jest-dom/extend-expect'],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
};