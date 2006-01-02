#!/usr/bin/env python
import os
import zpt

open('test.pt', 'w').write("""\
<html>
<body>
  <p tal:content="foo" />
</body>
</html>
""")

pt = zpt.PageTemplate('test.pt')
output = pt.render({'foo':'bar'})
assert output == """\
<html>
<body>
  <p>bar</p>
</body>
</html>
"""

os.remove('test.pt')