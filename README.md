# Python tools for Football Manager 24

Learning project.

## FM_role_score.py

The `FM_role_score.py` script is designed to simplify the process of evaluating the ability of players in certain roles in Football Manager 24. Much like in real football, players in Football Manager have the flexibility to assume various roles across different positions. However, the suitability of each role depends on the individual attributes of the players.

Attribute values expressed as intervals are converted to their lowest value, while unknown values (represented by '-') are converted to 1.

Every role in Football Manager requires a unique set of attributes, categorized as blue and green. The calculations are based on the fact that green attributes are worth more than blue ones.