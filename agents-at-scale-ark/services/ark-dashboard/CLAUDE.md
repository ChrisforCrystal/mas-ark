## Guidelines

### General
- Never look outside this current directory or its children
- After a change, always run `npm run build` to make sure the code is valid TS
- Before making a suggestion, always ask "will this really work" 
- Explain why making a change is going to work before suggesting it

### File names
- Always use kebab-case for file names

### Types
- Where possible, define types formally.  Do not do type definitions in function headers
- Where possible avoid using "any"
- Where possible refrain from using "as" to convert an unknown or any into a type
- Generated types are in lib/api/generated/types.ts

### Services
- Services should always be objects that export async functions.   
- Services are defined in lib/services
- Services should always use the generated types in lib/api/generated
