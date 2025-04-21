from django import forms
from django.forms import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Submit, Div
from .models import Verse

class VerseForm(forms.ModelForm):
    class Meta:
        model = Verse
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        
        # Get existing lines if editing
        initial_lines = []
        if self.instance.pk:
            initial_lines = [
                {
                    'line': line.content,
                    'syllables': line.syllable_count,
                    'grade': line.grade,
                    'position': line.position,
                }
                for line in self.instance.lines.all().order_by('position')
            ]
        
        # Ensure at least one line for new verses
        if not initial_lines:
            initial_lines = [{'line': '', 'syllables': 0, 'grade': 50, 'position': 1}]
        
        # Create the layout
        self.helper.layout = Layout(
            Field('title', css_class='mb-3'),
            HTML('<div id="verse-lines">'),
            *[self._create_line_layout(line) for line in initial_lines],
            HTML('</div>'),
            HTML('''
                <div class="mb-3">
                    <button type="button" class="btn btn-outline-primary" id="add-line">
                        <i class="bi bi-plus-lg"></i> Add Line
                    </button>
                </div>
            '''),
            Div(
                Submit('submit', 'Save Verse', css_class='btn-primary'),
                css_class='text-end'
            )
        )

    def _create_line_layout(self, line_data):
        position = line_data['position']
        return HTML(f'''
            <div class="verse-line mb-3 p-3 border rounded" data-position="{position}">
                <div class="row">
                    <div class="col">
                        <div class="mb-2">
                            <label class="form-label">Line {position}</label>
                            <input type="text" class="form-control" name="line_{position}" 
                                   value="{line_data['line']}">
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="text-muted small d-flex align-items-center gap-3">
                                <div>
                                    Syllables: <span class="badge bg-secondary syllable-count">
                                        {line_data['syllables']}
                                    </span>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input override-check" type="checkbox" 
                                           id="override_{position}">
                                    <label class="form-check-label" for="override_{position}">
                                        Override
                                    </label>
                                </div>
                                <div class="syllable-input d-none">
                                    <input type="number" class="form-control form-control-sm d-inline-block" 
                                           style="width: 80px;" name="syllables_{position}" 
                                           value="{line_data['syllables']}" min="1" max="99">
                                </div>
                            </div>
                            <div>
                                <label class="form-label me-2">Grade (1-99):</label>
                                <input type="number" class="form-control form-control-sm d-inline-block" 
                                       style="width: 80px;" name="grade_{position}" 
                                       value="{line_data['grade']}" min="1" max="99" required>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        ''')

    def save(self, commit=True):
        verse = super().save(commit=False)
        
        if commit:
            verse.save()
            
            # Get all form data
            form_data = self.data
            
            # Find all line inputs (they start with 'line_')
            line_positions = sorted([
                int(key.split('_')[1])
                for key in form_data.keys()
                if key.startswith('line_')
            ])
            
            # Delete existing lines
            verse.lines.all().delete()
            
            # Create new lines
            for position in line_positions:
                content = form_data.get(f'line_{position}', '').strip()
                if content:  # Only create lines with content
                    verse.lines.create(
                        content=content,
                        position=position,
                        syllable_count=form_data.get(f'syllables_{position}', 0),
                        grade=form_data.get(f'grade_{position}', 50)
                    )
        
        return verse 