# Code Syntax Highlighting

```bash
# List themes
pandoc --list-highlight-styles

# Apply theme
pandoc input.md -o output.pdf --highlight-style=tango
pandoc input.md -o output.html --highlight-style=monochrome
```

## Themes

| Theme | Best For |
|-------|----------|
| `tango` | General use (default) |
| `monochrome` | B&W printing |
| `espresso` | Dark background |
| `zenburn` | Soft colors |
| `breezedark` | Dark mode |

## Language Support

Use language identifiers after opening backticks:

```markdown
    ```python
    def hello():
        print("Hello")
    ```

    ```javascript
    const x = () => console.log("Hi");
    ```

    ```bash
    echo "Hello"
    ```
```

## Common Identifiers

| Language | Identifier |
|----------|------------|
| Python | `python`, `py` |
| JavaScript | `javascript`, `js` |
| TypeScript | `typescript`, `ts` |
| Bash | `bash`, `sh` |
| Go | `go`, `golang` |
| Rust | `rust`, `rs` |
| C++ | `cpp`, `c++` |
| Java | `java` |
| YAML | `yaml`, `yml` |
| JSON | `json` |

## Options

```bash
--no-highlight          # Disable highlighting
--from=markdown+task_lists  # Enable task lists (GFM)
```

## Attributes

```markdown
    ```{.python .numberLines}
    # Numbered lines
    code here
    ```

    ```{.python .numberLines startFrom="10"}
    # Start from line 10
    ```
```
