from enum import Enum

class Actions(Enum):
  KILL = "kill"
  BEAT_UP = "beat up"
  INSULT = "insult"
  CONVERSE = "converse"
  NONE = "none"

  @property
  def is_witnessed(self):
    if self in [Actions.KILL, Actions.BEAT_UP]:
      return True
    else:
      return False
