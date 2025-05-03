from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Verse, VerseLine
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import VerseForm
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from icecream import ic
from django.views.decorators.http import require_http_methods
import json

# Create your views here.

class VerseListView(ListView):
    model = Verse
    template_name = 'versus/verse_list.html'
    context_object_name = 'verses'

class VerseCreateView(LoginRequiredMixin, CreateView):
    model = Verse
    form_class = VerseForm
    template_name = 'versus/verse_form.html'

    @transaction.atomic
    def form_valid(self, form):
        ic("Form submission received")
        # Save the verse first
        self.object = form.save()
        ic("Verse saved:", self.object)

        # Get line data from POST
        line_data = {}
        max_position = 0
        
        # First collect all line data
        ic("POST data:", self.request.POST)
        for key in self.request.POST:
            if key.startswith('line_'):
                try:
                    position = int(key.split('_')[1])
                    content = self.request.POST.get(key, '').strip()
                    ic(f"Processing line {position}:", content)
                    if content:  # Only add non-empty lines
                        line_data[position] = {
                            'content': content,
                            'grade': self.request.POST.get(f'grade_{position}', 50)
                        }
                        max_position = max(max_position, position)
                except (ValueError, IndexError) as e:
                    ic(f"Error processing line {key}:", e)
                    continue

        ic("Collected line data:", line_data)
        # Create lines with sequential positions
        if line_data:
            # Sort positions
            sorted_positions = sorted(line_data.keys())
            ic("Sorted positions:", sorted_positions)
            
            # Create lines with new sequential positions
            for new_position, old_position in enumerate(sorted_positions, 1):
                data = line_data[old_position]
                ic(f"Creating line {new_position} from position {old_position}:", data)
                VerseLine.objects.create(
                    verse=self.object,
                    content=data['content'],
                    position=new_position,
                    grade=data['grade']
                )

            # Update verse content
            self.object.content = '\n'.join(
                line_data[pos]['content'] 
                for pos in sorted_positions
            )
            ic("Updated verse content:", self.object.content)
            self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('versus:detail', kwargs={'slug': self.object.slug})

class VerseDetailView(DetailView):
    model = Verse
    template_name = 'versus/verse_detail.html'
    slug_url_kwarg = 'slug'

class VerseEditView(LoginRequiredMixin, View):
    template_name = 'versus/verse_form.html'
    form_class = VerseForm

    def get(self, request, slug):
        ic("Edit view GET request for slug:", slug)
        verse = get_object_or_404(Verse, slug=slug)
        form = self.form_class(instance=verse)
        
        # Get existing lines in order
        lines = verse.lines.all().order_by('position')
        ic("Found lines:", lines)
        
        context = {
            'form': form,
            'verse': verse,
            'existing_lines': [
                {
                    'content': line.content,
                    'position': line.position,
                    'grade': line.grade,
                    'syllable_count': line.syllable_count,
                    'is_syllable_override': line.is_syllable_override
                }
                for line in lines
            ]
        }
        ic("Context for template:", context)
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, slug):
        try:
            ic("Starting POST request in VerseEditView")
            verse = get_object_or_404(Verse, slug=slug)
            form = self.form_class(request.POST, instance=verse)
            
            if form.is_valid():
                ic("Form is valid, calling form.save()")
                verse = form.save()
                ic("Form save completed")
                
                messages.success(request, 'Verse updated successfully.')
                return redirect('versus:detail', slug=verse.slug)
            else:
                ic("Form is invalid:", form.errors)
                messages.error(request, 'Please correct the errors below.')
                return render(request, self.template_name, {'form': form})
                
        except Exception as e:
            ic("Error in view:", str(e))
            messages.error(request, f'Error saving verse: {str(e)}')
            return render(request, self.template_name, {'form': form})

@require_http_methods(["POST"])
def save_verse_pattern(request, verse_id):
    try:
        ic("Saving verse pattern for verse_id:", verse_id)
        data = json.loads(request.body)
        verse = get_object_or_404(Verse, id=verse_id)
        
        if 'pattern' not in data:
            ic("Pattern not found in request data")
            return JsonResponse({
                'status': 'error',
                'message': 'Pattern is required'
            }, status=400)
        
        ic("Updating pattern:", data['pattern'])
        verse.pattern = data['pattern']
        verse.save()
        
        ic("Pattern saved successfully")
        return JsonResponse({
            'status': 'success',
            'message': 'Pattern saved successfully'
        })
    except Verse.DoesNotExist:
        ic("Verse not found:", verse_id)
        return JsonResponse({
            'status': 'error',
            'message': 'Verse not found'
        }, status=404)
    except json.JSONDecodeError:
        ic("Invalid JSON in request body")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        ic("Error saving pattern:", str(e))
        return JsonResponse({
            'status': 'error',
            'message': f'Error saving pattern: {str(e)}'
        }, status=400)

@require_http_methods(["POST"])
def save_verse_line(request, verse_id, line_id):
    try:
        data = json.loads(request.body)
        verse = Verse.objects.get(id=verse_id)
        
        if line_id.startswith('new_'):
            # Create new line
            line = VerseLine.objects.create(
                verse=verse,
                content=data['content'],
                grade=data['grade'],
                syllable_count=data['syllable_count'],
                position=data['position']
            )
        else:
            # Update existing line
            line = VerseLine.objects.get(id=line_id, verse=verse)
            line.content = data['content']
            line.grade = data['grade']
            line.syllable_count = data['syllable_count']
            line.position = data['position']
            line.save()
            
        return JsonResponse({'status': 'success', 'line_id': line.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
