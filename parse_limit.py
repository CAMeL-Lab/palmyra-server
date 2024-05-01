

def get_lines_to_parse(lines, word_limit):
    
    sentence_limit = None
    for i, line in enumerate(lines):
        print(line)
        print(f'limit before {word_limit}')
        word_limit -= len(line.split())
        print(f'limit after {word_limit}')
        if word_limit < 0:
            sentence_limit = i
            break
    if not sentence_limit:
        sentence_limit = len(lines)
    print(f'sentence limit: {sentence_limit}')
    return lines[:sentence_limit], lines[sentence_limit:]

if __name__ == '__main__':
    lines = ['test line 1', 'test line 2', 'test line 3', 'test line 4']
    
    word_limit = 8
    
    lines_to_parse, lines_to_ignore = get_lines_to_parse(lines, word_limit)
    print(lines_to_parse)
    print()
    print(lines_to_ignore)
    import pdb; pdb.set_trace()