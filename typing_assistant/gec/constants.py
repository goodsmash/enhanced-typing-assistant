"""Constants for GEC module"""

# Default model configurations
DEFAULT_MODEL_CONFIGS = {
    'roberta': {
        'name': 'roberta-base',
        'vocab_path': 'vocab/roberta_vocab.txt',
        'labels_path': 'vocab/labels.txt',
        'max_len': 128,
        'min_len': 3,
        'lowercase': True,
        'tp_prob': 0.9,
        'fp_prob': 0.1
    },
    'xlnet': {
        'name': 'xlnet-base-cased',
        'vocab_path': 'vocab/xlnet_vocab.txt',
        'labels_path': 'vocab/labels.txt',
        'max_len': 128,
        'min_len': 3,
        'lowercase': False,
        'tp_prob': 0.9,
        'fp_prob': 0.1
    }
}

# Error type mappings
ERROR_TYPES = {
    'VERB:FORM': ['VBZ', 'VBD', 'VBG', 'VBN'],
    'VERB:TENSE': ['VBD', 'VBZ', 'VB'],
    'VERB:SVA': ['VBZ', 'VB'],
    'NOUN:NUM': ['NNS', 'NN'],
    'NOUN:POSS': ["'s", "s'"],
    'DET': ['a', 'an', 'the'],
    'PREP': ['in', 'on', 'at', 'for', 'to', 'with'],
    'PUNCT': [',', '.', '!', '?', ';', ':'],
    'SPELL': [],  # Handled by edit distance
    'WO': []  # Word order, handled by sequence labeling
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    'VERB:FORM': 0.8,
    'VERB:TENSE': 0.85,
    'VERB:SVA': 0.9,
    'NOUN:NUM': 0.85,
    'NOUN:POSS': 0.9,
    'DET': 0.8,
    'PREP': 0.85,
    'PUNCT': 0.95,
    'SPELL': 0.7,
    'WO': 0.95
}

# Cache settings
DEFAULT_CACHE_SIZE = 1000
CACHE_EXPIRY_SECONDS = 3600  # 1 hour
