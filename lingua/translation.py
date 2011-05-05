"""
File: translation.py

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
from django.db.models import signals
import handler
from django.utils.translation import activate, deactivate
from django.utils.translation import ugettext_lazy as _

signals.post_init.connect(handler.post_init)

class Translation(object):

    def contribute_to_class(self, main_cls, name):
        """Get translation fields and convert them then the class is ready
           Django set the model fields as attributes 
        """        
        from django.conf import settings
        _languages = dict(settings.__dict__.get('LANGUAGES', {}))

        translation_fields = [x for x in [x.lower() for x in self.__dict__ if '__' not in x] ]

        for x in translation_fields:
            main_cls.add_to_class(x, self.__dict__[x])

        def _getattr(klass, name):
            if '_' in name:
                lang, v = name.split('_')[::-1][0], name.split('_')[::-1][1]
                
                if lang in _languages:
                    activate(lang)
                    value = unicode(_(getattr(klass,v)))                
                    deactivate()

                    return value
            return klass.__class__.__getattribute__(klass, name)

        main_cls.add_to_class('_translation_fields', tuple(translation_fields))
        main_cls.add_to_class('_languages', _languages)     
        main_cls.add_to_class('__getattr__', _getattr)

    contribute_to_class = classmethod(contribute_to_class)
