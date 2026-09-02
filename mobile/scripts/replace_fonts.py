import os

directory = r"c:\Users\NITOR 5\Desktop\FYP\mobile\app"

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'Inter_' in content:
                content = content.replace('Inter_400Regular', 'Poppins_400Regular')
                content = content.replace('Inter_500Medium', 'Poppins_500Medium')
                content = content.replace('Inter_600SemiBold', 'Poppins_600SemiBold')
                content = content.replace('Inter_700Bold', 'Poppins_700Bold')
                content = content.replace('Inter_800ExtraBold', 'Poppins_800ExtraBold')
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated fonts in {file}")

print("All fonts updated!")
