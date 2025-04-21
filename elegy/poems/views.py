from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import Poem, PoemLine
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class PoemListView(ListView):
    model = Poem
    template_name = 'poems/poem_list.html'
    context_object_name = 'poems'

class PoemCreateView(LoginRequiredMixin, CreateView):
    model = Poem
    template_name = 'poems/poem_form.html'
    fields = ['title']

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # Get all line data from the form
        line_positions = []
        for key in self.request.POST:
            if key.startswith('line_'):
                try:
                    position = int(key.split('_')[1])
                    line_positions.append(position)
                except (ValueError, IndexError):
                    continue

        # Sort positions to maintain order
        line_positions.sort()

        # Create lines in order
        for position in line_positions:
            content = self.request.POST.get(f'line_{position}', '').strip()
            grade = self.request.POST.get(f'grade_{position}', 50)
            syllable_override = self.request.POST.get(f'syllables_{position}')

            # Create the line even if content is empty
            line = PoemLine.objects.create(
                poem=form.instance,
                position=position,
                content=content,
                grade=grade
            )

            # Set syllable override if provided
            if syllable_override:
                try:
                    line.syllable_count = int(syllable_override)
                    line.is_syllable_override = True
                    line.save()
                except ValueError:
                    pass

        return response

    def get_success_url(self):
        return reverse_lazy('poems:detail', kwargs={'pk': self.object.pk})

class PoemDetailView(DetailView):
    model = Poem
    template_name = 'poems/poem_detail.html'

class PoemEditView(View):
    template_name = 'poems/poem_edit.html'

    def get(self, request, pk):
        poem = get_object_or_404(Poem, pk=pk)
        # Create lines if they don't exist
        if not poem.lines.exists():
            lines = poem.content.split('\n')
            for i, content in enumerate(lines, 1):
                PoemLine.objects.create(
                    poem=poem,
                    content=content,  # Don't strip whitespace
                    position=i,
                    grade=50  # Default grade
                )
        return render(request, self.template_name, {'poem': poem})

    def post(self, request, pk):
        try:
            poem = get_object_or_404(Poem, pk=pk)
            
            # Update title
            poem.title = request.POST.get('title')
            if not poem.title:
                messages.error(request, 'Title is required.')
                return render(request, self.template_name, {'poem': poem})
            
            poem.save()
            
            # Get all line data from the form
            line_data = {}
            max_position = 0
            
            # First, collect all line positions
            for key in request.POST:
                if key.startswith('line_'):
                    position = int(key.split('_')[1])
                    max_position = max(max_position, position)
                    line_data[position] = {'content': request.POST[key]}
            
            # Then collect associated data for each line
            for key, value in request.POST.items():
                if key.startswith('grade_'):
                    position = int(key.split('_')[1])
                    if position in line_data:
                        line_data[position]['grade'] = int(value)
                elif key.startswith('syllables_'):
                    position = int(key.split('_')[1])
                    if position in line_data:
                        line_data[position]['syllable_count'] = int(value)
                        line_data[position]['is_syllable_override'] = True

            if not line_data:
                messages.error(request, 'At least one line is required.')
                return render(request, self.template_name, {'poem': poem})

            # Delete all existing lines to handle reordering
            poem.lines.all().delete()

            # Create lines in the new order, including empty ones
            for position in range(1, max_position + 1):
                if position in line_data:
                    line = PoemLine(
                        poem=poem,
                        position=position,
                        content=line_data[position]['content'],
                        grade=line_data[position].get('grade', 50)
                    )
                    if 'syllable_count' in line_data[position] and line_data[position].get('is_syllable_override', False):
                        line.syllable_count = line_data[position]['syllable_count']
                        line.is_syllable_override = True
                    line.save()

            # Update poem content
            all_lines = poem.lines.order_by('position')
            poem.content = '\n'.join(line.content for line in all_lines)
            poem.save()

            messages.success(request, 'Poem updated successfully.')
            return redirect('poems:detail', pk=poem.pk)
            
        except Exception as e:
            messages.error(request, f'Error saving poem: {str(e)}')
            return render(request, self.template_name, {'poem': poem})
