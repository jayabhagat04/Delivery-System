from pathlib import Path

path = Path('delivery_system.py')
text = path.read_text(encoding='utf-8')
text = text.replace('&quot;', '"')
text = text.replace('&#039;', "'")
text = text.replace('&lt;', '<')
text = text.replace('&gt;', '>')
text = text.replace('&amp;', '&')
path.write_text(text, encoding='utf-8')
print('replaced')
