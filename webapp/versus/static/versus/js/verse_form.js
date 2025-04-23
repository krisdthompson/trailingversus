document.addEventListener('DOMContentLoaded', function() {
    // Initialize Sortable for drag-and-drop
    const linesContainer = document.querySelector('#lines-container');
    if (linesContainer) {
        new Sortable(linesContainer, {
            handle: '.drag-handle',
            animation: 150,
            onEnd: function() {
                // Update position values after drag
                updatePositions();
            }
        });
    }

    // Function to update position values
    function updatePositions() {
        document.querySelectorAll('.verse-line').forEach((line, index) => {
            const position = index + 1;
            line.dataset.position = position;
            
            // Update all field names and IDs with new position
            line.querySelectorAll('input').forEach(input => {
                const fieldType = input.name.split('-')[1]; // content, grade, etc.
                input.name = `line_${position}-${fieldType}`;
                if (input.id) {
                    input.id = `id_line_${position}-${fieldType}`;
                }
            });
            
            // Update label 'for' attributes
            line.querySelectorAll('label').forEach(label => {
                if (label.getAttribute('for')) {
                    const fieldType = label.getAttribute('for').split('-')[2];
                    label.setAttribute('for', `id_line_${position}-${fieldType}`);
                }
            });
        });
    }

    // Function to count syllables
    function countSyllables(word) {
        word = word.toLowerCase();
        word = word.replace(/[^a-z]/g, '');
        
        // Handle special cases
        word = word.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '');
        word = word.replace(/^y/, '');
        
        // Count syllables
        return word.match(/[aeiouy]{1,2}/g)?.length || 0;
    }

    // Function to update syllable count
    function updateSyllableCount(lineElement) {
        const content = lineElement.querySelector('input[name$="-content"]').value;
        const words = content.split(/\s+/);
        const syllableCount = words.reduce((count, word) => count + countSyllables(word), 0);
        const badge = lineElement.querySelector('.syllable-badge');
        if (badge) {
            badge.textContent = syllableCount;
        }
        
        // Update hidden syllable count if not overridden
        const overrideCheck = lineElement.querySelector('input[name$="-is_syllable_override"]');
        const syllableInput = lineElement.querySelector('input[name$="-syllable_count"]');
        if (overrideCheck && !overrideCheck.checked && syllableInput) {
            syllableInput.value = syllableCount;
        }
    }

    // Function to create a new verse line element
    function createVerseLine(position) {
        const lineId = `new_${position}`;
        const template = `
            <div class="verse-line mb-3 p-3 border border-2 border-brown rounded bg-light" data-position="${position}">
                <i class="bi bi-grip-vertical drag-handle"></i>
                <div class="row align-items-center g-3">
                    <div class="col-md-6">
                        <input type="text" name="line_${lineId}-content" 
                               class="form-control verse-line-input" placeholder="Enter your verse line">
                    </div>
                    <div class="col-md-4">
                        <div class="syllable-controls">
                            <div class="d-flex align-items-center mb-2">
                                <span class="me-2">Syllables:</span>
                                <span class="badge bg-texas-brown text-white syllable-badge">0</span>
                            </div>
                            <div class="d-flex align-items-center">
                                <div class="form-check form-check-inline mb-0">
                                    <input type="checkbox" name="line_${lineId}-is_syllable_override" 
                                           class="form-check-input" id="id_line_${lineId}-is_syllable_override">
                                    <label class="form-check-label ms-2" for="id_line_${lineId}-is_syllable_override">Override</label>
                                </div>
                                <div class="syllable-input ms-2 d-none">
                                    <input type="number" name="line_${lineId}-syllable_count" value="0"
                                           class="form-control form-control-sm text-center">
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="grade-control">
                            <label class="form-label mb-1">Grade</label>
                            <input type="number" name="line_${lineId}-grade" value="50"
                                   class="form-control form-control-sm text-center" min="1" max="99">
                        </div>
                    </div>
                    <input type="hidden" name="line_${lineId}-position" value="${position}">
                </div>
            </div>
        `;
        const div = document.createElement('div');
        div.innerHTML = template.trim();
        return div.firstChild;
    }

    // Handle syllable override checkbox changes
    document.addEventListener('change', function(e) {
        if (e.target.matches('input[name$="-is_syllable_override"]')) {
            const syllableInput = e.target.closest('.verse-line').querySelector('.syllable-input');
            if (syllableInput) {
                syllableInput.classList.toggle('d-none', !e.target.checked);
            }
        }
    });

    // Handle content changes for syllable counting
    document.addEventListener('input', function(e) {
        if (e.target.matches('input[name$="-content"]')) {
            updateSyllableCount(e.target.closest('.verse-line'));
        }
    });

    // Initialize syllable counts for existing lines
    document.querySelectorAll('.verse-line').forEach(line => {
        updateSyllableCount(line);
    });

    // Handle Add Line button
    const addLineButton = document.getElementById('add-line');
    if (addLineButton) {
        addLineButton.addEventListener('click', function() {
            const linesContainer = document.getElementById('lines-container');
            const newPosition = linesContainer.children.length + 1;
            
            // Create and add new line
            const newLine = createVerseLine(newPosition);
            linesContainer.appendChild(newLine);
            
            // Initialize syllable count for new line
            updateSyllableCount(newLine);
        });
    }
}); 