"""
File: admin.py

Copyright (c) aquarianhouse.com | Georg Kasmin.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from django.contrib import admin
from django import forms
import os, sys
import polib

class LinguaModelAdmin(admin.ModelAdmin):

    @staticmethod
    def get_fields_with_type(model, fields_type):
        fields = []
        for field in model._translation_fields:
            for l in model._languages.keys():
                name = '_'.join((field, l))
                field_type = fields_type[field]
                fields.append( (name, field_type.__class__() ) )
        return fields

    @staticmethod
    def get_fields(model):
        return ['_'.join((field, l)) for field in model._translation_fields for l in model._languages.keys()]


    def get_form(self, request, obj=None, **kwargs):
        form = super(LinguaModelAdmin, self).get_form(request, obj, **kwargs)
        
        class LinguaAdminForm(form):
            def __init__(self, *args, **kwargs):
                super(LinguaAdminForm, self).__init__(*args, **kwargs)
                instance = kwargs["instance"]
                fields_type = dict([(x, self.fields[x]) for x in instance._translation_fields])
                fields = LinguaModelAdmin.get_fields_with_type(self._meta.model, fields_type)

                #create field dynamically
                for x, y in fields:
                    self.fields[x] = y

                #make sure the original value will be shown
                for x in instance._translation_fields:
                    self.initial[x] = getattr(instance, "_".join( (x,'00') ))

                self.initial.update(dict( [ (x, getattr(instance, x)) for x,y in fields] ))

            def save(self, *args, **kwargs):
                model = super(LinguaAdminForm, self).save(*args, **kwargs)
                from django.conf import settings
                from lingua.utils import clear_gettext_cache

                #TODO make pretty
                if settings.SETTINGS_MODULE is not None:
                    parts = settings.SETTINGS_MODULE.split('.')
                    project = __import__(parts[0])
                    self.projectpath = os.path.join(os.path.dirname(project.__file__), 'locale')
                    self.languages_po = {}
                    for l in dict(settings.LANGUAGES).keys():
                        p = os.path.join(self.projectpath, l, 'LC_MESSAGES', 'django.po') 
                        if os.path.exists(p):                   
                            self.languages_po[l] = polib.pofile(p)

                for f in model._translation_fields:
                    msgid = getattr(model, "_".join((f,"00")))
                    for l in model._languages:
                        field = "_".join((f,l))
                        c = self.cleaned_data.get(field, None)
                        if l in self.languages_po:
                            po = self.languages_po[l]
                            po_entry = po.find(msgid)
                            if po_entry:
                                po_entry.msgstr = c
                            else:
                                entry = polib.POEntry(msgid=msgid, msgstr=c)
                                po.append(entry)

                for k,p in self.languages_po.items():
                    p.save()
                    path = os.path.join(self.projectpath, k, 'LC_MESSAGES', 'django.mo')
                    p.save_as_mofile(path)

                #reset gettext cache
                clear_gettext_cache()

                return model

        return LinguaAdminForm

    def get_fieldsets(self, request, obj=None):
        fields = super(LinguaModelAdmin,self).get_fieldsets(request,obj)
        form = self.get_form(request, obj)
        model = form._meta.model
        fields[0][1]["fields"] += LinguaModelAdmin.get_fields(model)
        return fields


