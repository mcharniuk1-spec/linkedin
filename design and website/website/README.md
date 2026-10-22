# Editable website and Storybook source

See ../README.md for setup and current-release limits. website-v3/ is the current V9 application; its historical folder name is retained for imports. packages/ contains shared UI, motion, generated tokens, V3 catalogues and V5 showcase/content/video sources. .storybook/ uses the same shared components and ../assets/public.

The source package is portable and has no private enquiry backend. The current form is an inactive static preview. npm run build regenerates tokens from ../design-system/ and builds the current app into dist/. npm run build:storybook builds the shared component library separately. No local absolute path is required by runtime code.
