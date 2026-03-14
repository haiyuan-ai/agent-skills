# Math and Equations

```bash
# PDF (native)
pandoc input.md -o output.pdf --pdf-engine=xelatex

# HTML with MathJax
pandoc input.md -o output.html --mathjax

# HTML with KaTeX (faster)
pandoc input.md -o output.html --katex

# Word (auto-converts to OMML)
pandoc input.md -o output.docx
```

## Syntax

```markdown
Inline: $E = mc^2$

Block:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

Aligned:
$$
\begin{align}
x &= y + z \\
a &= b \times c
\end{align}
$$

Cases:
$$
f(x) = \begin{cases}
x^2 & \text{if } x > 0 \\
0 & \text{otherwise}
\end{cases}
$$
```

## Common Symbols

| Symbol | LaTeX |
|--------|-------|
| $\alpha$ | `\alpha` |
| $\sum$ | `\sum` |
| $\int$ | `\int` |
| $\infty$ | `\infty` |
| $\leq$ | `\leq` |
| $\rightarrow$ | `\rightarrow` |
| $\nabla$ | `\nabla` |
| $\partial$ | `\partial` |
