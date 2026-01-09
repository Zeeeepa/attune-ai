# Tweet 3: Code Comparison Visual Asset

This visual shows the before/after transformation for Tweet 3 in the v3.9.1 campaign.

---

## Visual Asset: Side-by-Side Code Comparison

### Format Options

#### Option 1: Text-Based (Twitter-Native, Copy-Paste)

```
❌ VULNERABLE CODE              ✅ SECURE CODE

def save_config(path):          from empathy_os.config
    with open(path, 'w') as f:  import _validate_file_path
        json.dump(data, f)
                                def save_config(path):
⚠️ CWE-22: Path traversal          validated =
Attacker: ../../etc/passwd         _validate_file_path(path)
                                   with validated.open('w') as f:
                                       json.dump(data, f)

                                ✅ 174 security tests
                                ✅ 0 vulnerabilities
```

#### Option 2: Image (For Maximum Impact)

**Recommended tool**: Carbon.now.sh or similar code screenshot tool

**Left Side (Red Background)**:
```python
# ❌ VULNERABLE CODE

def save_config(user_path: str, data: dict):
    with open(user_path, 'w') as f:
        json.dump(data, f)

# ⚠️ CWE-22: Path Traversal
# Attacker can write to:
#   ../../etc/passwd
#   /etc/cron.d/backdoor
```

**Right Side (Green Background)**:
```python
# ✅ SECURE CODE

from empathy_os.config import _validate_file_path

def save_config(user_path: str, data: dict):
    validated_path = _validate_file_path(user_path)
    with validated_path.open('w') as f:
        json.dump(data, f)

# ✅ Blocks path traversal
# ✅ Blocks null bytes
# ✅ Blocks system directories
# ✅ 174 security tests
```

---

## Creating the Image

### Using Carbon.now.sh

1. Go to https://carbon.now.sh
2. Use these settings:
   - Theme: Monokai
   - Background: true
   - Drop shadow: true
   - Font: Fira Code
   - Font size: 14px

3. Create TWO images:

**Image 1 (Vulnerable):**
- Background color: `#2D0E0E` (dark red)
- Paste the vulnerable code
- Export as PNG (2x)

**Image 2 (Secure):**
- Background color: `#0E2D0E` (dark green)
- Paste the secure code
- Export as PNG (2x)

4. Combine side-by-side using:
   - Figma (free)
   - Canva (free)
   - ImageMagick: `convert +append vulnerable.png secure.png comparison.png`

### Using Figma (Recommended)

**Template**: 1200x628px (Twitter optimal)

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  ❌ VULNERABLE CODE  │  ✅ SECURE CODE          │
├─────────────────────┼──────────────────────────┤
│                     │                          │
│  [Code block with   │  [Code block with        │
│   red background]   │   green background]      │
│                     │                          │
│  ⚠️ CWE-22          │  ✅ 174 tests            │
│  Path Traversal     │  ✅ 0 vulnerabilities    │
│                     │                          │
└─────────────────────┴──────────────────────────┘
```

**Colors**:
- Vulnerable side: `#2D0E0E` background, `#FF6B6B` accent
- Secure side: `#0E2D0E` background, `#6BFF6B` accent
- Text: `#F8F8F2` (high contrast)

---

## Alt Text (Accessibility)

```
Side-by-side Python code comparison. Left shows vulnerable code with bare open() function susceptible to path traversal (CWE-22). Right shows secure code using _validate_file_path() with 174 security tests and zero vulnerabilities.
```

---

## Quick Generation Script

If you want to generate this programmatically:

```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

def create_code_comparison():
    """Create side-by-side code comparison image."""

    # Image dimensions
    width, height = 1200, 628
    img = Image.new('RGB', (width, height), color='#1A1A1A')
    draw = ImageDraw.Draw(img)

    # Try to use monospace font, fallback to default
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Monaco.ttf', 14)
        header_font = ImageFont.truetype('/System/Library/Fonts/Monaco.ttf', 18)
    except:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    # Left side (vulnerable) - Red background
    draw.rectangle([(0, 0), (595, height)], fill='#2D0E0E')
    draw.text((20, 20), "❌ VULNERABLE CODE", fill='#FF6B6B', font=header_font)

    vulnerable_code = """def save_config(path):
    with open(path, 'w') as f:
        json.dump(data, f)

⚠️ CWE-22: Path Traversal
Attacker: ../../etc/passwd"""

    y_offset = 60
    for line in vulnerable_code.split('\n'):
        draw.text((20, y_offset), line, fill='#F8F8F2', font=font)
        y_offset += 25

    # Right side (secure) - Green background
    draw.rectangle([(605, 0), (width, height)], fill='#0E2D0E')
    draw.text((625, 20), "✅ SECURE CODE", fill='#6BFF6B', font=header_font)

    secure_code = """from empathy_os.config
import _validate_file_path

def save_config(path):
    validated =
        _validate_file_path(path)
    with validated.open('w') as f:
        json.dump(data, f)

✅ 174 security tests
✅ 0 vulnerabilities"""

    y_offset = 60
    for line in secure_code.split('\n'):
        draw.text((625, y_offset), line, fill='#F8F8F2', font=font)
        y_offset += 25

    # Save
    img.save('docs/marketing/assets/tweet3_comparison.png')
    print("✅ Image created: docs/marketing/assets/tweet3_comparison.png")

if __name__ == '__main__':
    create_code_comparison()
```

**To run**:
```bash
pip install Pillow
python scripts/create_tweet_visual.py
```

---

## Fallback: Text-Only Tweet

If you don't have time to create an image, the text-based comparison above works great on Twitter. The emoji visual hierarchy (❌/✅) makes it scannable even without an image.

**Usage in Tweet 3**:
Post the text comparison as a reply to your own Tweet 3, or include it in an attached image using Twitter's text tweet screenshot feature.

---

## Image Upload Tips

1. **Upload as media**, not as a link (better preview)
2. **Add alt text** for accessibility
3. **Preview on mobile** before posting (most users see mobile first)
4. **Test contrast** - dark mode vs light mode
5. **Keep text large** - Twitter compresses images

---

**Status**: Template ready
**Recommended**: Use Carbon.now.sh for quick, professional code images
**Fallback**: Text-based comparison (works great!)
**Time to create**: 5-10 minutes with Carbon.now.sh
