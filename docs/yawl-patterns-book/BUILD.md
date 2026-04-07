# Building and Viewing This Book

This book is built with [mdBook](https://rust-lang.github.io/mdBook/), a utility for creating modern online books from Markdown files.

---

## Prerequisites

### Install mdBook

```bash
# macOS
brew install mdbook

# Linux
cargo install mdbook

# Or download from https://github.com/rust-lang/mdBook/releases
```

### Verify Installation

```bash
mdbook --version
# Output: mdbook v0.4.x
```

---

## Building the Book

### Quick Start

```bash
cd docs/yawl-patterns-book
mdbook build
```

This creates the `book/` directory with the generated HTML site.

### Development Mode (Live Preview)

```bash
mdbook serve
```

Then open your browser to:
- **http://localhost:3000**

The book will auto-reload as you edit files!

---

## Project Structure

```
docs/yawl-patterns-book/
├── book.toml           # mdBook configuration
├── src/
│   ├── SUMMARY.md       # Table of contents
│   ├── README.md        # Introduction
│   ├── *.md             # Chapter files
│   └── patterns/
│       ├── control-flow/
│       │   ├── sequence.md
│       │   ├── exclusive-choice.md
│       │   ├── parallel-split.md
│       │   └── ...
│       ├── advanced-branching/
│       ├── structural/
│       ├── state-based/
│       ├── multiple-instance/
│       ├── data/
│       └── resource/
└── book/               # Generated output (don't edit)
```

---

## Editing Patterns

### Pattern Template

Each pattern file follows this structure:

```markdown
# Pattern Name

> **Therefore**: [Alexander-style summary]

---

## Context
[The situation or environment]

## Problem
**[The question or issue]**

## Forces
[Conflicting considerations]

## Solution
[How to resolve it]

### POWL v2 Representation
[Code examples]

## Example
[Concrete business example]

## When to Use This Pattern
✅ Use when...
❌ Don't use when...

## Related Patterns
- [Pattern 1](./path/to/pattern1.md)
- [Pattern 2](./path/to/pattern2.md)

## Implementation Notes
[How to implement in POWL, BPMN, Petri nets]

## Quality Attributes
[Table of quality impacts]

## Common Mistakes
[Pitfalls and solutions]

## Pattern Combinations
[How this pattern combines with others]

## Multi-Perspective Extensions
[How to use for org, time, data perspectives]

## Exercises
[Practice problems]

## References
[Citations]
```

### Writing Guidelines

1. **Alexander Style**: Start with "Therefore:" summary that captures the essence
2. **Context First**: Describe when this pattern applies
3. **Problem as Question**: Frame as "How do you...?"
4. **Concrete Examples**: Use real business processes
5. **POWL Code**: Include executable POWL examples
6. **Related Patterns**: Link to patterns that form the language network

---

## Adding New Patterns

### 1. Create Pattern File

```bash
# Example: Add a new pattern to control-flow
touch src/patterns/control-flow/new-pattern.md
```

### 2. Write Pattern Content

Use the template above.

### 3. Update SUMMARY.md

Add the pattern to the appropriate section:

```markdown
## Control Flow Patterns (Basic)

## [New Pattern](./patterns/control-flow/new-pattern.md)
```

### 4. Test Locally

```bash
mdbook serve
# Open http://localhost:3000
```

### 5. Commit Changes

```bash
git add src/patterns/control-flow/new-pattern.md
git commit -m "docs: add New Pattern to workflow pattern language"
```

---

## Customizing the Book

### Themes

Edit `book.toml` to change themes:

```toml
[output.html]
default-theme = "light"  # or "navy", "coal", "ayu"
preferred-dark-theme = "navy"
```

### CSS Styling

Create `src/theme.css`:

```css
/* Custom pattern highlighting */
.pattern-box {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}
```

Enable in `book.toml`:

```toml
[output.html]
additional-css = ["theme.css"]
```

### Preprocessors

Add custom preprocessors in `book.toml`:

```toml
[preprocessor.pattern-links]
command = "python3 scripts/link-patterns.py"
```

---

## Deployment

### GitHub Pages

1. Build the book:
   ```bash
   mdbook build
   ```

2. Deploy to `gh-pages` branch:
   ```bash
   git subtree push --prefix book origin gh-pages
   ```

3. Enable GitHub Pages in repository settings

### Self-Hosted

1. Build the book:
   ```bash
   mdbook build
   ```

2. Serve with any web server:
   ```bash
   cd book
   python3 -m http.server 8000
   ```

### Continuous Deployment

Add to `.github/workflows/docs.yml`:

```yaml
name: Deploy Book

on:
  push:
    branches: [main]
    paths: ['docs/yawl-patterns-book/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install mdBook
        run: curl -L https://github.com/rust-lang/mdBook/releases/download/v0.4.21/mdbook-v0.4.21-x86_64-unknown-linux-gnu.tar.gz | tar xz
      - name: Build book
        run: ./mdbook build docs/yawl-patterns-book
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/yawl-patterns-book/book
```

---

## Contributing

We welcome contributions to this pattern language!

### Contribution Guidelines

1. **Follow Alexander Style**: Each pattern should have context, problem, solution format
2. **Include POWL Examples**: Show how to implement in POWL v2
3. **Add Multi-Perspective**: Consider org, time, data dimensions
4. **Link Related Patterns**: Build the language network
5. **Test Examples**: Verify POWL code runs without errors

### Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b pattern/my-new-pattern`
3. Write your pattern file
4. Update SUMMARY.md
5. Test locally: `mdbook serve`
6. Submit pull request

---

## Resources

- [mdBook Documentation](https://rust-lang.github.io/mdBook/)
- [Markdown Guide](https://www.markdownguide.org/)
- [POWL v2 Specification](https://pm4py.fit/)
- [YAWL Patterns Paper](https://www.workflowpatterns.com/)

---

## Troubleshooting

### mdBook Not Found

```bash
# Make sure mdBook is in your PATH
which mdbook

# If not, install or add to PATH
export PATH="$PATH:$HOME/.cargo/bin"
```

### Build Errors

```bash
# Check Markdown syntax
mdbook build --draft

# Look for broken links
mdbook build --open
```

### Missing Styles

```bash
# Clear cache and rebuild
rm -rf book/
mdbook build
```

---

**Happy pattern writing!** 🚀
