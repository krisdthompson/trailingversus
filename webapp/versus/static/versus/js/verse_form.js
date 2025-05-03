document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');

    // Get CSRF token
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    console.log('CSRF Token Element:', csrfTokenElement);
    const csrfToken = csrfTokenElement ? csrfTokenElement.value : null;
    console.log('CSRF Token:', csrfToken);

    if (!csrfToken) {
        console.error('CSRF Token not found! Make sure {% csrf_token %} is in your template.');
    }

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    console.log('Found tooltip triggers:', tooltipTriggerList.length);
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Sortable for drag-and-drop
    const linesContainer = document.querySelector('#lines-container');
    console.log('Lines container found:', !!linesContainer);
    if (linesContainer) {
        new Sortable(linesContainer, {
            handle: '.drag-handle',
            animation: 150,
            onEnd: function() {
                updatePositions();
            }
        });
    }

    // Pattern Editor Functionality
    const patternDisplay = document.getElementById('pattern-display');
    const patternEditor = document.getElementById('pattern-editor');
    const patternActions = document.getElementById('pattern-actions');
    const editPatternBtn = document.querySelector('.pattern-editor .bi-pencil-square');
    const savePatternBtn = document.getElementById('save-pattern');
    const cancelPatternBtn = document.getElementById('cancel-pattern');

    console.log('Pattern Editor Elements:', {
        display: !!patternDisplay,
        editor: !!patternEditor,
        actions: !!patternActions,
        editBtn: !!editPatternBtn,
        saveBtn: !!savePatternBtn,
        cancelBtn: !!cancelPatternBtn
    });

    if (editPatternBtn) {
        editPatternBtn.addEventListener('click', function() {
            console.log('Edit pattern button clicked');
            patternDisplay.classList.add('d-none');
            patternEditor.classList.remove('d-none');
            patternActions.classList.remove('d-none');
            editPatternBtn.classList.add('d-none');
            patternEditor.focus();
        });
    }

    if (savePatternBtn) {
        savePatternBtn.addEventListener('click', async function() {
            console.log('Save pattern button clicked');
            const verseIdElement = document.querySelector('[name=verse_id]');
            console.log('Verse ID Element:', verseIdElement);
            const verseId = verseIdElement ? verseIdElement.value : null;
            console.log('Verse ID:', verseId);

            if (!verseId) {
                console.error('No verse ID found');
                alert('Cannot save pattern: No verse ID found');
                return;
            }

            if (!csrfToken) {
                console.error('No CSRF token found');
                alert('Cannot save pattern: No CSRF token found');
                return;
            }

            try {
                console.log('Sending pattern save request...');
                console.log('Pattern value:', patternEditor.value);
                
                const response = await fetch(`/versus/api/verse/${verseId}/pattern/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        pattern: patternEditor.value
                    })
                });

                console.log('Response status:', response.status);
                const data = await response.json();
                console.log('Response data:', data);

                if (response.ok && data.status === 'success') {
                    console.log('Pattern saved successfully');
                    patternDisplay.textContent = patternEditor.value;
                    patternDisplay.classList.remove('d-none');
                    patternEditor.classList.add('d-none');
                    patternActions.classList.add('d-none');
                    editPatternBtn.classList.remove('d-none');

                    // Show success feedback
                    const tooltip = bootstrap.Tooltip.getInstance(editPatternBtn);
                    if (tooltip) {
                        tooltip.dispose();
                    }
                    editPatternBtn.setAttribute('data-bs-title', 'Pattern saved successfully!');
                    editPatternBtn.classList.add('text-success');
                    new bootstrap.Tooltip(editPatternBtn).show();
                    setTimeout(() => {
                        const tooltip = bootstrap.Tooltip.getInstance(editPatternBtn);
                        if (tooltip) {
                            tooltip.dispose();
                        }
                        editPatternBtn.setAttribute('data-bs-title', 'Edit pattern');
                        editPatternBtn.classList.remove('text-success');
                        new bootstrap.Tooltip(editPatternBtn);
                    }, 2000);
                } else {
                    throw new Error(data.message || 'Failed to save pattern');
                }
            } catch (error) {
                console.error('Error saving pattern:', error);
                alert('Failed to save pattern. Please try again. Error: ' + error.message);
            }
        });
    }

    if (cancelPatternBtn) {
        cancelPatternBtn.addEventListener('click', function() {
            console.log('Cancel pattern button clicked');
            patternEditor.value = patternDisplay.textContent;
            patternDisplay.classList.remove('d-none');
            patternEditor.classList.add('d-none');
            patternActions.classList.add('d-none');
            editPatternBtn.classList.remove('d-none');
        });
    }

    // Function to update position values
    function updatePositions() {
        document.querySelectorAll('.verse-line').forEach((line, index) => {
            const position = index + 1;
            line.dataset.position = position;
            
            // Update all field names and IDs with new position
            line.querySelectorAll('input').forEach(input => {
                const fieldType = input.name.split('-')[1];
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

    // Function to save a verse line
    async function saveVerseLine(lineElement) {
        const verseId = document.querySelector('[name=verse_id]').value;
        const lineId = lineElement.dataset.lineId;
        const contentInput = lineElement.querySelector('input[name$="-content"]');
        const gradeInput = lineElement.querySelector('input[name$="-grade"]');
        const syllableInput = lineElement.querySelector('input[name$="-syllable_count"]');
        const saveIcon = lineElement.querySelector('.save-status');

        try {
            const response = await fetch(`/versus/api/verse/${verseId}/line/${lineId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    content: contentInput.value,
                    grade: gradeInput.value,
                    syllable_count: syllableInput.value,
                    position: lineElement.dataset.position
                })
            });

            if (response.ok) {
                contentInput.classList.remove('unsaved');
                contentInput.classList.add('saved');
                saveIcon.innerHTML = '<i class="bi bi-check-circle text-success"></i>';
                setTimeout(() => {
                    saveIcon.innerHTML = '<i class="bi bi-save"></i>';
                }, 2000);
            } else {
                throw new Error('Failed to save line');
            }
        } catch (error) {
            console.error('Error saving line:', error);
            contentInput.classList.remove('saved');
            contentInput.classList.add('unsaved');
            saveIcon.innerHTML = '<i class="bi bi-exclamation-circle text-danger"></i>';
        }
    }

    // Function to create a new verse line element
    function createVerseLine(position) {
        const lineId = `new_${position}`;
        const template = `
            <div class="verse-line mb-3 p-3 border border-2 border-brown rounded bg-light" data-position="${position}" data-line-id="${lineId}">
                <i class="bi bi-grip-vertical drag-handle"></i>
                <div class="row align-items-center g-3">
                    <div class="col-md-6 position-relative">
                        <input type="text" name="line_${lineId}-content" 
                               class="form-control verse-line-input" placeholder="Enter your verse line">
                        <div class="save-status">
                            <i class="bi bi-save"></i>
                        </div>
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

    // Add save button click handlers
    document.addEventListener('click', function(e) {
        if (e.target.closest('.save-status')) {
            const lineElement = e.target.closest('.verse-line');
            if (lineElement) {
                saveVerseLine(lineElement);
            }
        }
    });

    // Mark content as unsaved when changed
    document.addEventListener('input', function(e) {
        if (e.target.matches('input[name$="-content"]')) {
            const lineElement = e.target.closest('.verse-line');
            if (lineElement) {
                e.target.classList.remove('saved');
                e.target.classList.add('unsaved');
                updateSyllableCount(lineElement);
            }
        }
    });

    // Handle syllable override checkbox changes
    document.addEventListener('change', function(e) {
        if (e.target.matches('input[name$="-is_syllable_override"]')) {
            const syllableInput = e.target.closest('.verse-line').querySelector('.syllable-input');
            if (syllableInput) {
                syllableInput.classList.toggle('d-none', !e.target.checked);
            }
        }
    });

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