# Contributing to MomOps

Thank you for your interest in contributing to MomOps! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/momops.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Guidelines

### Code Style

- Use functional React components with hooks
- Follow the existing code structure and naming conventions
- Use meaningful variable and function names
- Add comments for complex logic
- Keep components focused and single-purpose

### Component Structure

```jsx
import { useState } from 'react'

function ComponentName({ prop1, prop2 }) {
  const [state, setState] = useState(initialValue)
  
  const handleAction = () => {
    // Handler logic
  }
  
  return (
    <div className="component-name">
      {/* JSX */}
    </div>
  )
}

export default ComponentName
```

### CSS Guidelines

- Use CSS variables defined in `:root` for colors
- Follow the existing naming convention (kebab-case)
- Keep styles organized by component
- Use responsive design principles
- Maintain the pastel color theme

### Testing

Before submitting a PR:
- Test all features you've modified
- Test on different screen sizes
- Verify data persistence in localStorage
- Check for console errors
- Test with sample data

## Feature Requests

Have an idea for a new feature? Great! Please:
1. Check if it's already been requested in Issues
2. Open a new issue with the "enhancement" label
3. Describe the feature and its benefits
4. Include mockups or examples if possible

## Bug Reports

Found a bug? Please:
1. Check if it's already been reported
2. Open a new issue with the "bug" label
3. Include:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots if applicable
   - Browser and OS information

## Pull Request Process

1. Update the README.md if needed
2. Ensure your code follows the style guidelines
3. Test your changes thoroughly
4. Write a clear PR description explaining:
   - What changes you made
   - Why you made them
   - How to test them

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

Thank you for contributing to MomOps! 🎉
