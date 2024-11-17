# Dictionary Resources

This directory contains dictionary files and word lists used for spell checking and text correction:

## Files
- `common_misspellings.txt`: Frequently misspelled words and their corrections
- `wiktionary_core.txt`: Core vocabulary from Wiktionary
- `contractions.txt`: Common English contractions and their expansions
- `internet_slang.txt`: Common internet slang and abbreviations
- `technical_terms.txt`: Technical and programming-related terms
- `domain_specific/`: Domain-specific vocabularies (medical, legal, etc.)

## Sources
1. Grammarly Wiktionary
2. Wikipedia Common Misspellings
3. OpenOffice Dictionary
4. Mozilla Firefox Dictionary
5. GNU Aspell Dictionary
6. Custom curated lists

## Format
Each dictionary file follows the format:
```
word<tab>correction[<tab>frequency_score]
```

Example:
```
recieve<tab>receive<tab>0.95
ur<tab>your<tab>0.8
btw<tab>by the way<tab>0.9
```

## Updates
The dictionaries are regularly updated from their respective sources using the `update_dictionaries.py` script.
