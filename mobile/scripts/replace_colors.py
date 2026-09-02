import os

files = [
    r"c:\Users\NITOR 5\Desktop\FYP\mobile\app\(auth)\welcome.tsx",
    r"c:\Users\NITOR 5\Desktop\FYP\mobile\app\(auth)\register.tsx",
    r"c:\Users\NITOR 5\Desktop\FYP\mobile\app\(auth)\login.tsx",
    r"c:\Users\NITOR 5\Desktop\FYP\mobile\app\(auth)\complete-profile.tsx"
]

replacements = {
    '#704F38': '#111111',
    '#B0A090': '#9E9E9E',
    '#E6DFD9': '#EEEEEE',
    '#EFEFEF': '#EEEEEE'
}

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old_color, new_color in replacements.items():
            content = content.replace(old_color, new_color)
            
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {os.path.basename(file)}")
    except Exception as e:
        print(f"Error processing {file}: {e}")

print("All done!")
