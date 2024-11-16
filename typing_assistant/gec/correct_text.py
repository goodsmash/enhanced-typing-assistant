import sys
import json
import argparse
from dictionary import DictionaryManager

def parse_args():
    parser = argparse.ArgumentParser(description='Text correction service')
    parser.add_argument('--text', required=True, help='Text to correct')
    parser.add_argument('--domain', default='general', help='Domain for correction')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Initialize dictionary manager
    dict_manager = DictionaryManager()
    
    # Get corrections
    corrections = dict_manager.get_corrections(args.text, domain=args.domain)
    
    # Format corrections for JSON output
    formatted_corrections = [
        {
            'correction': corr.correction,
            'confidence': corr.confidence,
            'original': corr.original
        }
        for corr in corrections
    ]
    
    # Output as JSON
    print(json.dumps(formatted_corrections))

if __name__ == '__main__':
    main()
