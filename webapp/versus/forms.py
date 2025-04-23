from django import forms
from django.forms import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Submit, Div, Row, Column
from .models import Verse, VerseLine
from icecream import ic

class VerseLineForm(forms.Form):
    content = forms.CharField(
        required=False,  # Allow empty lines
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your verse line'
        })
    )
    grade = forms.IntegerField(
        min_value=1, 
        max_value=99,
        initial=50 ,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'style': 'width: 100px;'
        })
    )
    syllable_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-sm',
            'style': 'width: 100px;'
        })
    )
    is_syllable_override = forms.BooleanField(
        required=False,
        label='Override',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    position = forms.IntegerField(widget=forms.HiddenInput())

class VerseForm(forms.ModelForm):
    class Meta:
        model = Verse
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        self.helper.form_id = 'verse-form'
        
        # Create the layout
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<h2 class="text-brown mb-0">{% if form.instance.id %}Edit{% else %}Add{% endif %} Verse</h2>'),
                    HTML('''
                        {% if form.instance.id %}
                            <a href="{% url 'versus:detail' form.instance.slug %}" class="btn btn-outline-secondary">
                                <i class="bi bi-arrow-left"></i> Back to Verse
                            </a>
                        {% else %}
                            <a href="{% url 'versus:list' %}" class="btn btn-outline-secondary">
                                <i class="bi bi-arrow-left"></i> Back to Trail Verses
                            </a>
                        {% endif %}
                    '''),
                    css_class='d-flex justify-content-between align-items-center mb-4'
                ),
                Field('title', css_class='form-control mb-4'),
                HTML('<div id="lines-container" class="sortable">'),
                # Display existing verse lines if editing
                HTML('''
                    {% if form.instance.id %}
                        {% for line in form.instance.lines.all %}
                        <div class="verse-line mb-3 p-3 border border-2 border-brown rounded bg-light" data-position="{{ line.position }}">
                            <i class="bi bi-grip-vertical drag-handle"></i>
                            <div class="row align-items-center g-3">
                                <div class="col-md-8">
                                    <input type="text" name="line_{{ line.id }}-content" value="{{ line.content }}" 
                                           class="form-control verse-line-input" placeholder="Enter your verse line">
                                </div>
                                <div class="col-md-3">
                                    <div class="syllable-controls">
                                        <div class="d-flex align-items-center mb-2">
                                            <span class="me-2">Syllables:</span>
                                            <span class="badge bg-texas-brown text-white syllable-badge">{{ line.syllable_count }}</span>
                                        </div>
                                        <div class="d-flex align-items-center">
                                            <div class="form-check form-check-inline mb-0">
                                                <input type="checkbox" name="line_{{ line.id }}-is_syllable_override" 
                                                       class="form-check-input" id="id_line_{{ line.id }}-is_syllable_override"
                                                       {% if line.is_syllable_override %}checked{% endif %}>
                                                <label class="form-check-label ms-2" for="id_line_{{ line.id }}-is_syllable_override">Override</label>
                                            </div>
                                            <div class="syllable-input ms-2 {% if not line.is_syllable_override %}d-none{% endif %}">
                                                <input type="number" name="line_{{ line.id }}-syllable_count" 
                                                       value="{{ line.syllable_count }}" class="form-control form-control-sm text-center">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-1">
                                    <div class="grade-control">
                                        <label class="form-label mb-1">Grade</label>
                                        <input type="number" name="line_{{ line.id }}-grade" value="{{ line.grade }}"
                                               class="form-control form-control-sm text-center no-spinner" 
                                               min="1" max="99" style="width: 4ch;">
                                    </div>
                                </div>
                                <input type="hidden" name="line_{{ line.id }}-position" value="{{ line.position }}">
                            </div>
                        </div>
                        {% endfor %}
                    {% endif %}
                '''),
                HTML('</div>'),
                Div(
                    HTML('''
                        <button type="button" class="btn btn-outline-brown" id="add-line">
                            <i class="bi bi-plus-lg"></i> Add Line
                        </button>
                    '''),
                    css_class='mb-3'
                ),
                Div(
                    Submit('submit', 'Save Verse', css_class='btn bg-brown text-white'),
                    css_class='text-end'
                ),
                css_class='container py-4'
            )
        )

    def save(self, commit=True):
        ic("Starting VerseForm.save() method")
        verse = super().save(commit=False)
        
        if commit:
            ic("Saving verse initial:", verse)
            verse.save()
            
            # Get the form data
            ic("Processing form data:", self.data)
            
            # Track new position for each line
            current_position = 1
            
            # Process all form fields to find line content fields
            content_fields = [k for k in self.data.keys() if k.startswith('line_') and k.endswith('-content')]
            ic("Found content fields:", content_fields)
            
            for key in content_fields:
                ic("Processing content field:", key)
                # Get the line identifier (either a PK or new_X)
                line_id = key.split('-')[0].replace('line_', '')
                content = self.data[f'line_{line_id}-content'].strip()
                
                if not content:  # Skip empty lines
                    ic(f"Skipping empty line {line_id}")
                    continue
                
                # Get the form values
                try:
                    grade = int(self.data.get(f'line_{line_id}-grade', 50))
                    is_override = self.data.get(f'line_{line_id}-is_syllable_override') == 'on'
                    syllable_count = int(self.data.get(f'line_{line_id}-syllable_count', 0))
                    
                    line_data = {
                        'content': content,
                        'grade': grade,
                        'position': current_position
                    }
                    
                    if is_override:
                        line_data['syllable_count'] = syllable_count
                        line_data['is_syllable_override'] = True
                    
                    ic(f"Line {line_id} data:", line_data)
                    
                    # Create or update the line
                    if line_id.isdigit():
                        try:
                            line = verse.lines.get(pk=int(line_id))
                            ic(f"Found existing line {line_id}")
                            for field, value in line_data.items():
                                setattr(line, field, value)
                            if is_override:
                                line._skip_syllable_count = True
                            line.save()
                            ic(f"Updated line {line_id}:", line)
                        except VerseLine.DoesNotExist:
                            ic(f"Line {line_id} not found, creating new")
                            line = VerseLine(verse=verse, **line_data)
                            if is_override:
                                line._skip_syllable_count = True
                            line.save()
                            ic(f"Created new line for {line_id}:", line)
                    else:  # This is a new line
                        ic(f"Creating new line for {line_id}")
                        line = VerseLine(verse=verse, **line_data)
                        if is_override:
                            line._skip_syllable_count = True
                        line.save()
                        ic(f"Created new line:", line)
                    
                    current_position += 1
                except Exception as e:
                    ic(f"Error processing line {line_id}:", str(e))
                    raise
            
            # Update verse content
            lines = verse.lines.all().order_by('position')
            ic("All lines after processing:", list(lines))
            verse.content = '\n'.join(line.content for line in lines)
            verse.save()
            ic("Final verse content:", verse.content)
            
        return verse 