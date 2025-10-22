# tours/management/commands/translate_content.py
import os
import re
from html import unescape
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from modeltranslation.translator import translator
from google.cloud import translate_v2 as translate

class Command(BaseCommand):
    help = 'Translates model fields, preserving variables.'

    def handle(self, *args, **options):
        if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            raise CommandError('Google credentials are not set.')

        translate_client = translate.Client()
        target_languages = [lang[0] for lang in settings.LANGUAGES if lang[0] != settings.LANGUAGE_CODE]
        registered_models = translator.get_registered_models()

        variable_re = re.compile(
            r'({{\s*[^}]+?\s*}})|(%\([^)]+\)[diouxXeEfFgGcrs%])|(%\w)|(<[^>]+>)'
        )

        for model in registered_models:
            model_name = model.__name__
            opts = translator.get_options_for_model(model)
            translatable_fields = opts.fields

            self.stdout.write(self.style.SUCCESS(f'--- Translating model: {model_name} ---'))
            for obj in model.objects.all():
                self.stdout.write(f'  Processing {model_name} ID: {obj.pk}')

                for field in translatable_fields:
                    original_value = getattr(obj, field)
                    if not original_value or not isinstance(original_value, str) or len(original_value.strip()) == 0:
                        continue

                    variables = variable_re.findall(original_value)
                    placeholders = {f'v{i}': ''.join(var) for i, var in enumerate(variables)}

                    temp_text = original_value
                    for key, val in placeholders.items():
                        temp_text = temp_text.replace(val, f'<span class="notranslate">{key}</span>')

                    for lang_code in target_languages:
                        # --- هذا هو السطر المهم الذي تم تعديله ---
                        db_lang_code = lang_code.replace('-', '_')
                        lang_field_name = f"{field}_{db_lang_code}"

                        if not getattr(obj, lang_field_name):
                            try:
                                translation = translate_client.translate(
                                    temp_text,
                                    target_language=lang_code,
                                    source_language=settings.LANGUAGE_CODE,
                                    format_='html'
                                )
                                translated_text = unescape(translation['translatedText'])

                                for key, val in placeholders.items():
                                    placeholder_pattern = re.compile(f'<span class="notranslate">{key}</span>')
                                    translated_text = placeholder_pattern.sub(val, translated_text)

                                setattr(obj, lang_field_name, translated_text)
                                self.stdout.write(f'    - Translated "{field}" to "{lang_code}"')
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'    - Could not translate "{field}" to "{lang_code}". Error: {e}'))
                obj.save()

        self.stdout.write(self.style.SUCCESS('--- Database content translation finished. ---'))