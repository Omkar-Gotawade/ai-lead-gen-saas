path = r'D:/lead gen/frontend/src/pages/LandingPage.jsx'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 32 (index 31)
lines[31] = "    desc: \"Track open rates, reply rates, and conversions with a live dashboard. Know exactly what is working.\",\n"

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed line 32')
