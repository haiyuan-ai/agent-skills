#!/usr/bin/env python3
"""
Mermaid Style Themes Configuration
Built-in professional themes for mermaid-to-png.
"""

from typing import Dict, Any, Optional, List

# =============================================================================
# Style Theme Definitions
# =============================================================================

STYLES: Dict[str, Dict[str, Any]] = {
    "dark-tech": {
        "name": "Dark Technology",
        "description": "Dark background with neon accents, perfect for technical architecture diagrams",
        "theme_variables": {
            "primaryColor": "#1a1a2e",
            "primaryTextColor": "#eee",
            "primaryBorderColor": "#16213e",
            "lineColor": "#0f3460",
            "secondaryColor": "#e94560",
            "tertiaryColor": "#533483",
            "background": "#1a1a2e",
            "mainBkg": "#1a1a2e",
            "secondBkg": "#16213e",
            "nodeBorder": "#0f3460",
            "clusterBkg": "#16213e",
            "clusterBorder": "#0f3460",
            "titleColor": "#eee",
            "edgeLabelBackground": "#1a1a2e",
            "nodeTextColor": "#eee"
        },
        "flowchart": {
            "htmlLabels": True,
            "curve": "basis",
            "padding": 20
        },
        "background": "#1a1a2e",
        "font_family": "Inter, system-ui, -apple-system, sans-serif"
    },

    "fresh-business": {
        "name": "Fresh Business",
        "description": "Clean, professional look with subtle blues - perfect for business presentations",
        "theme_variables": {
            "primaryColor": "#e8f4f8",
            "primaryTextColor": "#2c3e50",
            "primaryBorderColor": "#3498db",
            "lineColor": "#95a5a6",
            "secondaryColor": "#ecf0f1",
            "tertiaryColor": "#f39c12",
            "background": "#ffffff",
            "mainBkg": "#e8f4f8",
            "secondBkg": "#f8fafb",
            "nodeBorder": "#3498db",
            "clusterBkg": "#f8fafb",
            "clusterBorder": "#bdc3c7",
            "titleColor": "#2c3e50",
            "edgeLabelBackground": "#ffffff",
            "nodeTextColor": "#2c3e50"
        },
        "flowchart": {
            "htmlLabels": True,
            "curve": "cardinal",
            "padding": 15
        },
        "background": "#ffffff",
        "font_family": "Segoe UI, Roboto, -apple-system, sans-serif"
    },

    "hand-drawn": {
        "name": "Hand-drawn Sketch",
        "description": "Sketch-like appearance for brainstorming and early concept diagrams",
        "theme_variables": {
            "primaryColor": "#fff9e6",
            "primaryTextColor": "#5d4e37",
            "primaryBorderColor": "#8b7355",
            "lineColor": "#a0926b",
            "secondaryColor": "#f5f0e1",
            "tertiaryColor": "#d4c4a8",
            "background": "#fff9e6",
            "mainBkg": "#fff9e6",
            "secondBkg": "#f5f0e1",
            "nodeBorder": "#8b7355",
            "clusterBkg": "#f5f0e1",
            "clusterBorder": "#a0926b",
            "titleColor": "#5d4e37",
            "edgeLabelBackground": "#fff9e6",
            "nodeTextColor": "#5d4e37"
        },
        "flowchart": {
            "htmlLabels": True,
            "curve": "stepAfter",
            "padding": 20
        },
        "background": "#fff9e6",
        "font_family": "Comic Sans MS, cursive, sans-serif"
    },

    "gradient-modern": {
        "name": "Gradient Modern",
        "description": "Vibrant gradients and modern colors for eye-catching presentations",
        "theme_variables": {
            "primaryColor": "#667eea",
            "primaryTextColor": "#ffffff",
            "primaryBorderColor": "#764ba2",
            "lineColor": "#a78bfa",
            "secondaryColor": "#f093fb",
            "tertiaryColor": "#f5576c",
            "background": "#1a1a2e",
            "mainBkg": "#667eea",
            "secondBkg": "#764ba2",
            "nodeBorder": "#a78bfa",
            "clusterBkg": "#1e1b4b",
            "clusterBorder": "#4c1d95",
            "titleColor": "#ffffff",
            "edgeLabelBackground": "#1a1a2e",
            "nodeTextColor": "#ffffff"
        },
        "flowchart": {
            "htmlLabels": True,
            "curve": "basis",
            "padding": 25
        },
        "background": "#1a1a2e",
        "font_family": "SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif"
    }
}

# =============================================================================
# Chart Type Specific Configurations
# =============================================================================

CHART_TYPE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "flowchart": {
        "curve": "basis",
        "padding": 20,
        "useMaxWidth": True
    },
    "sequence": {
        "diagramMarginX": 50,
        "diagramMarginY": 10,
        "actorMargin": 50,
        "width": 150,
        "height": 65,
        "boxMargin": 10,
        "boxTextMargin": 5,
        "noteMargin": 10,
        "messageMargin": 35
    },
    "gantt": {
        "titleTopMargin": 25,
        "barHeight": 20,
        "barGap": 4,
        "topPadding": 50,
        "leftPadding": 75,
        "gridLineStartPadding": 35,
        "fontSize": 11,
        "numberSectionStyles": 4
    },
    "class": {
        "diagramMarginX": 50,
        "diagramMarginY": 10,
        "actorMargin": 50,
        "width": 150,
        "height": 65,
        "boxMargin": 10,
        "boxTextMargin": 5,
        "noteMargin": 10,
        "messageMargin": 35
    },
    "state": {
        "diagramMarginX": 50,
        "diagramMarginY": 10,
        "actorMargin": 50,
        "width": 150,
        "height": 65,
        "boxMargin": 10,
        "boxTextMargin": 5,
        "noteMargin": 10,
        "messageMargin": 35
    }
}

# =============================================================================
# Utility Functions
# =============================================================================

def get_style_config(style_name: str) -> Optional[Dict[str, Any]]:
    """Get style configuration by name."""
    return STYLES.get(style_name)

def get_available_styles() -> List[str]:
    """Get list of available style names."""
    return list(STYLES.keys())

def get_style_info(style_name: str) -> Optional[Dict[str, str]]:
    """Get style human-readable info."""
    style = STYLES.get(style_name)
    if style:
        return {
            "name": style["name"],
            "description": style["description"]
        }
    return None

def generate_mermaid_config(style_name: Optional[str] = None, chart_type: str = "flowchart") -> str:
    """
    Generate Mermaid configuration JSON for the given style and chart type.
    Returns the config as a string to be injected into the diagram.
    """
    config_parts = []

    # Add init directive
    config_parts.append('%%{init: {')

    settings = []

    # Add theme variables if style is specified
    if style_name and style_name in STYLES:
        style = STYLES[style_name]
        theme_vars = style.get("theme_variables", {})

        if theme_vars:
            settings.append(f"  'themeVariables': {str(theme_vars).replace(chr(39), chr(34))}")

        # Add flowchart-specific settings
        flowchart_config = style.get("flowchart", {})
        if flowchart_config:
            settings.append(f"  'flowchart': {str(flowchart_config).replace(chr(39), chr(34))}")

        # Add chart type specific config
        chart_config = CHART_TYPE_CONFIGS.get(chart_type, {})
        if chart_config:
            settings.append(f"  '{chart_type}': {str(chart_config).replace(chr(39), chr(34))}")

    config_parts.append(','.join(settings))
    config_parts.append('}}%%')

    return '\n'.join(config_parts)

def inject_style_into_diagram(diagram_code: str, style_name: Optional[str] = None, chart_type: str = "flowchart") -> str:
    """
    Inject style configuration into Mermaid diagram code.
    """
    if not style_name or style_name not in STYLES:
        return diagram_code

    # Generate config
    config = generate_mermaid_config(style_name, chart_type)

    # Check if diagram already has init directive
    if "%%{init:" in diagram_code:
        # Replace existing init directive
        pattern = r'%%\{init:.*?\}%%\s*'
        diagram_code = re.sub(pattern, config + '\n', diagram_code, flags=re.DOTALL)
    else:
        # Add config at the beginning
        diagram_code = config + '\n' + diagram_code

    return diagram_code


if __name__ == "__main__":
    # Print available styles
    print("Available Mermaid Styles:")
    print("-" * 50)
    for style_name in get_available_styles():
        info = get_style_info(style_name)
        if info:
            print(f"\n{style_name}:")
            print(f"  Name: {info['name']}")
            print(f"  Description: {info['description']}")
