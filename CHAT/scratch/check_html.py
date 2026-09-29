from html.parser import HTMLParser

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
        self.errors = []
        
    def handle_starttag(self, tag, attrs):
        if tag not in self.void_tags:
            self.stack.append((tag, self.getpos()))
            
    def handle_endtag(self, tag):
        if tag in self.void_tags:
            return
        if not self.stack:
            self.errors.append(f"Unexpected closing tag </{tag}> at {self.getpos()}")
            return
        last_tag, pos = self.stack.pop()
        if last_tag != tag:
            self.errors.append(f"Mismatched tag: expected </{last_tag}> (from {pos}), got </{tag}> at {self.getpos()}")

with open('desktop_app/templates/index.html', encoding='utf-8') as f:
    content = f.read()

checker = TagChecker()
checker.feed(content)

print(f"Errors found: {len(checker.errors)}")
for e in checker.errors[:10]:
    print(" ", e)
print(f"Unclosed tags in stack: {len(checker.stack)}")
for t, pos in checker.stack:
    print(f"  Unclosed <{t}> from {pos}")
