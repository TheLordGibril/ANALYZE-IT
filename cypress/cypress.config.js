const { defineConfig } = require("cypress");

const baseUrl = process.env.CYPRESS_BASE_URL
// const baseUrl = 'http://localhost:3000';

console.log(`--------------------------------------------: ${baseUrl}`);
console.log(`Using base URL: ${baseUrl}`);
console.log(`--------------------------------------------: ${baseUrl}`);

module.exports = defineConfig({
  e2e: {
    baseUrl,
    setupNodeEvents(on, config) {
      require('@cypress/code-coverage/task')(on, config)
      return config
    },
    env: {
      codeCoverage: {
        url: `${baseUrl}/__coverage__`
      }
    },
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    setupNodeEvents(on, config) {
      require('@cypress/code-coverage/task')(on, config)
      return config
    }
  }
});
