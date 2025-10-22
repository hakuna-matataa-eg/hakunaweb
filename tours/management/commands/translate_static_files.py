# tours/management/commands/translate_static_files.py
import os
import re
import polib
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
from google.cloud import translate_v2 as translate
from html import unescape

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class Command(BaseCommand):
    help = 'Translates static .po files using Google Translate API, preserving variables.'

    def handle(self, *args, **kwargs):
        if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            raise CommandError('Google credentials are not set.')

        translate_client = translate.Client()
        locale_path = settings.LOCALE_PATHS[0]
        languages = [lang[0] for lang in settings.LANGUAGES if lang[0] != 'en']
        
        # Regex to find Django template variables, python format specifiers
        variable_re = re.compile(
            r'({{\s*[^}]+?\s*}})|(%\([^)]+\)[diouxXeEfFgGcrs%])|(%\w)'
        )

        for lang_code in languages:
            po_file_path = os.path.join(locale_path, lang_code, 'LC_MESSAGES', 'django.po')
            
            if not os.path.exists(po_file_path):
                self.stdout.write(self.style.WARNING(f'File not found for "{lang_code}", skipping.'))
                continue

            self.stdout.write(f'Processing {po_file_path}...')
            po = polib.pofile(po_file_path)

            entries_to_translate = [entry for entry in po if not entry.msgstr and entry.msgid]
            if not entries_to_translate:
                self.stdout.write(self.style.SUCCESS(f'No new strings to translate for "{lang_code}".'))
                continue
            
            entry_chunks = list(chunks(entries_to_translate, 100))
            self.stdout.write(f'Found {len(entries_to_translate)} strings. Translating in {len(entry_chunks)} chunk(s)...')

            for i, chunk in enumerate(entry_chunks):
                self.stdout.write(f'  - Translating chunk {i+1}/{len(entry_chunks)}...')
                
                texts_for_api = []
                placeholders_map = []

                for entry in chunk:
                    variables = variable_re.findall(entry.msgid)
                    placeholders = {f'v{j}': ''.join(var) for j, var in enumerate(variables)}
                    
                    temp_text = entry.msgid
                    for key, val in placeholders.items():
                        temp_text = temp_text.replace(val, f'<span class="notranslate">{key}</span>')
                    
                    texts_for_api.append(temp_text)
                    placeholders_map.append(placeholders)
                
                translations = translate_client.translate(
                    texts_for_api,
                    target_language=lang_code,
                    source_language='en',
                    format_='html' # <-- نخبر جوجل أن يتعامل مع النص كـ HTML
                )

                for entry, translation, placeholders in zip(chunk, translations, placeholders_map):
                    translated_text = unescape(translation['translatedText'])
                    
                    for key, val in placeholders.items():
                        # Use regex for safer replacement
                        placeholder_pattern = re.compile(f'<span class="notranslate">{key}</span>')
                        translated_text = placeholder_pattern.sub(val, translated_text)
                    
                    entry.msgstr = translated_text

            po.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully translated and saved for "{lang_code}".'))

        self.stdout.write('Compiling message files...')
        try:
            call_command('compilemessages')
            self.stdout.write(self.style.SUCCESS('All translations complete.'))
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Compilemessages failed. Check errors above.\n{e}'))