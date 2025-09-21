"""
LensLogic branding and ASCII art utilities
"""

LENSLOGIC_LOGO = """
 ██▓    ▓█████  ███▄    █   ██████  ██▓     ▒█████    ▄████  ██▓ ▄████▄
▓██▒    ▓█   ▀  ██ ▀█   █ ▒██    ▒ ▓██▒    ▒██▒  ██▒ ██▒ ▀█▒▓██▒▒██▀ ▀█
▒██░    ▒███   ▓██  ▀█ ██▒░ ▓██▄   ▒██░    ▒██░  ██▒▒██░▄▄▄░▒██▒▒▓█    ▄
▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒  ▒   ██▒▒██░    ▒██   ██░░▓█  ██▓░██░▒▓▓▄ ▄██▒
░██████▒░▒████▒▒██░   ▓██░▒██████▒▒░██████▒░ ████▓▒░░▒▓███▀▒░██░▒ ▓███▀ ░
░ ▒░▓  ░░░ ▒░ ░░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░░ ▒░▓  ░░ ▒░▒░▒░  ░▒   ▒ ░▓  ░ ░▒ ▒  ░
░ ░ ▒  ░ ░ ░  ░░ ░░   ░ ▒░░ ░▒  ░ ░░ ░ ▒  ░  ░ ▒ ▒░   ░   ░  ▒ ░  ░  ▒
  ░ ░      ░      ░   ░ ░ ░  ░  ░    ░ ░   ░ ░ ░ ▒  ░ ░   ░  ▒ ░░
    ░  ░   ░  ░         ░       ░      ░  ░    ░ ░        ░  ░  ░ ░
                                                              ░

    Smart photo & video organization powered by metadata
"""

LENSLOGIC_COMPACT = """
    ██▓    ▓█████  ███▄    █   ██████  ██▓     ▒█████    ▄████  ██▓ ▄████▄
   ▓██▒    ▓█   ▀  ██ ▀█   █ ▒██    ▒ ▓██▒    ▒██▒  ██▒ ██▒ ▀█▒▓██▒▒██▀ ▀█
   ▒██░    ▒███   ▓██  ▀█ ██▒░ ▓██▄   ▒██░    ▒██░  ██▒▒██░▄▄▄░▒██▒▒▓█    ▄
   ▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒  ▒   ██▒▒██░    ▒██   ██░░▓█  ██▓░██░▒▓▓▄ ▄██▒
   ░██████▒░▒████▒▒██░   ▓██░▒██████▒▒░██████▒░ ████▓▒░░▒▓███▀▒░██░▒ ▓███▀ ░
    Smart photo & video organization powered by metadata
"""

CAMERA_ASCII = """
    ╔══════════════════════════════════════╗
    ║                                      ║
    ║  📸🎬 LensLogic                      ║
    ║     Smart photo & video organization ║
    ║     powered by metadata              ║
    ║                                      ║
    ╚══════════════════════════════════════╝
"""

SIMPLE_LOGO = """
  ┌─ LensLogic ─────────────────────────────┐
  │ 📸🎬 Smart photo & video organization   │
  │     powered by metadata                 │
  └─────────────────────────────────────────┘
"""

def print_logo(style="compact"):
    """Print LensLogic logo in specified style"""
    if style == "full":
        print(LENSLOGIC_LOGO)
    elif style == "compact":
        print(LENSLOGIC_COMPACT)
    elif style == "camera":
        print(CAMERA_ASCII)
    elif style == "simple":
        print(SIMPLE_LOGO)
    else:
        print(LENSLOGIC_COMPACT)

def get_version_info():
    """Get version and build information"""
    return """
    Version: 1.0.0
    Build: Production
    License: MIT
    """

def print_startup_banner():
    """Print startup banner with logo and version"""
    print_logo("compact")
    print(get_version_info())