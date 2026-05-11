import os
import glob
import re

icon_map = {
    'bicycle': 'bike',
    'times': 'x',
    'times-circle': 'x-circle',
    'exclamation-circle': 'alert-circle',
    'exclamation-triangle': 'alert-triangle',
    'euro-sign': 'euro',
    'envelope': 'mail',
    'user-plus': 'user-plus',
    'clipboard-list': 'clipboard-list',
    'history': 'history',
    'users': 'users',
    'user': 'user',
    'phone': 'phone',
    'edit': 'edit',
    'trash': 'trash',
    'save': 'save',
    'search': 'search',
    'plus': 'plus',
    'check': 'check',
    'check-circle': 'check-circle',
    'filter': 'filter',
    'lock': 'lock',
    'arrow-left': 'arrow-left'
}

def replace_icons(match):
    classes = match.group(1)
    fa_match = re.search(r'fa-([a-zA-Z0-9\-]+)', classes)
    if not fa_match:
        return match.group(0)
    
    fa_name = fa_match.group(1)
    other_classes = re.sub(r'fas?\s+|fa-[a-zA-Z0-9\-]+\s*', '', classes).strip()
    
    lucide_name = icon_map.get(fa_name, fa_name)
    
    if other_classes:
        return f'<i data-lucide="{lucide_name}" class="{other_classes}">'
    else:
        return f'<i data-lucide="{lucide_name}">'

template_dir = r"c:\Users\r3d4\.gemini\antigravity\scratch\cyclorent\location\templates\location"

for filepath in glob.glob(os.path.join(template_dir, "*.html")):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace the FontAwesome script with Lucide script
    content = content.replace(
        '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">',
        '<script src="https://unpkg.com/lucide@latest"></script>\n    <style>.lucide { width: 1.25em; height: 1.25em; vertical-align: -0.125em; }</style>'
    )
    
    # Replace icons
    new_content = re.sub(r'<i class="([^"]*)"></i>', lambda m: replace_icons(m) + '</i>', content)
    
    # Special cases for icons that were not empty e.g. <i class="..."> </i> (none in our case but good to be safe)
    # Actually my regex above requires </i> immediately after, which is standard.
    
    # Add initialize script at the end of body
    if (filepath.endswith('base.html') or filepath.endswith('login.html')) and '<script>lucide.createIcons();</script>' not in new_content:
        new_content = new_content.replace('</body>', '<script>lucide.createIcons();</script>\n</body>')
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Icons replaced with Lucide successfully.")
