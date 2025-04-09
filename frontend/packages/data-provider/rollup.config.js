const typescript = require("rollup-plugin-typescript2");
const resolve = require("@rollup/plugin-node-resolve");
const json = require("@rollup/plugin-json");
const pkg = require("./package.json");
const peerDepsExternal = require("rollup-plugin-peer-deps-external");
const commonjs = require("@rollup/plugin-commonjs");
const replace = require("@rollup/plugin-replace");
const terser = require("@rollup/plugin-terser");
const generatePackageJson = require("rollup-plugin-generate-package-json");
const babel = require("@rollup/plugin-babel");

const plugins = [
  peerDepsExternal(),
  json(),
  resolve(),
  replace({
    preventAssignment: true,
    values: {
      __IS_DEV__: JSON.stringify(process.env.NODE_ENV === "development"),
    },
  }),
  commonjs(),
  // Move typescript2 plugin BEFORE babel to ensure declaration emit
  typescript({
    tsconfig: "./tsconfig.json",
    useTsconfigDeclarationDir: true,
    clean: true,
  }),
  babel({
    babelHelpers: "bundled",
    extensions: [".js", ".jsx", ".ts", ".tsx"],
    presets: [
      "@babel/preset-env",
      "@babel/preset-typescript",
      "@babel/preset-react",
    ],
    exclude: "node_modules/**",
  }),
  terser(),
];

const subfolderPlugins = (folderName) => [
  ...plugins,
  generatePackageJson({
    baseContents: {
      name: `${pkg.name}/${folderName}`,
      private: true,
      main: "../index.js",
      module: "./index.es.js", // Adjust to match the output file
      types: `../${folderName}/index.d.ts`, // Updated to point inside dist directory
    },
  }),
];

module.exports = [
  {
    input: "src/index.ts",
    output: [
      {
        file: pkg.main,
        format: "cjs",
        sourcemap: true,
        exports: "named",
      },
      {
        file: pkg.module,
        format: "esm",
        sourcemap: true,
        exports: "named",
      },
    ],
    ...{
      external: [
        ...Object.keys(pkg.dependencies || {}),
        ...Object.keys(pkg.devDependencies || {}),
        ...Object.keys(pkg.peerDependencies || {}),
        "react",
        "react-dom",
      ],
      preserveSymlinks: true,
      plugins,
    },
  },
  // Separate bundle for react-query related part
  {
    input: "src/react-query/index.ts",
    output: [
      {
        file: "dist/react-query/index.es.js",
        format: "esm",
        exports: "named",
        sourcemap: true,
      },
      {
        file: "dist/react-query/index.js",
        format: "cjs",
        exports: "named",
        sourcemap: true,
      },
    ],
    external: [
      ...Object.keys(pkg.dependencies || {}),
      ...Object.keys(pkg.devDependencies || {}),
      ...Object.keys(pkg.peerDependencies || {}),
      "react",
      "react-dom",
      // 'librechat-data-provider', // Marking main part as external
    ],
    preserveSymlinks: true,
    plugins: subfolderPlugins("react-query"),
  },
];
