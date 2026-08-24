import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['test/**/*.test.ts'],
    // The sweep tests grind a lot of float math; give them room.
    testTimeout: 120_000,
    hookTimeout: 120_000,
  },
});
