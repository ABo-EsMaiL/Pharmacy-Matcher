import unicodedata
import re

sample = '11494 ﺏ32 - ﻣﺠﻢ 90 ﺍﻓﻴﺮﻭﻛﻮﻛﺴﻴﺐ 228.00 0.00 030'
norm = unicodedata.normalize('NFKD', sample)
print('Normalized:', repr(norm))

# Test regex extraction of the drug name
# Line format: <CODE> <ITEM_NAME> <PRICE> <VALUE> <QUANTITY>
# e.g.: 11494 ﺏ32 - ﻣﺠﻢ 90 ﺍﻓﻴﺮﻭﻛﻮﻛﺴﻴﺐ 228.00 0.00 030
m = re.match(r"^\s*\d+\s+(.*?)\s+\d+\.\d{2}\s+\d+\.\d{2}\s+\d+", norm)
if m:
    print('Extracted name:', repr(m.group(1).strip()))
