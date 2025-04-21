def count_syllables(word):
    """
    A simple syllable counter for English text.
    This is a basic implementation and may not be 100% accurate for all cases.
    """
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if not word:
        return 0
        
    # Count groups of vowels (including 'y')
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    
    # Handle silent e
    if word.endswith('e'):
        count -= 1
    
    # Handle special cases
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        count += 1
        
    return max(1, count)  # Every word has at least one syllable 