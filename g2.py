import os
import gkeepapi

EMAIL = os.environ["GKEEP_EMAIL"]
MASTER_TOKEN = os.environ["GKEEP_MASTER_TOKEN"]

keep = gkeepapi.Keep()
ok = keep.authenticate(EMAIL, MASTER_TOKEN)
print("authenticate:", ok)

keep.sync()
print("Total notes:", len(keep.all()))

