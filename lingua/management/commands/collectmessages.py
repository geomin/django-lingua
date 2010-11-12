"""
File: collectmessages.py

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
from django.core.management import BaseCommand, CommandError
from django.db import models
from django.utils.encoding import smart_str

class Command(BaseCommand):
    help = "Translate database messages"

    requires_model_validation = False

    def handle(self, *args, **options):
        db_values = []
        """ Taken from django.core.management.commands.syncdb"""
        for app in models.get_apps():
            model_list = models.get_models(app, include_auto_created=True)

            """Performance is not so important, we do it once... """
            for m in model_list:
                if hasattr(m, '_translation_fields'):
                    for x in m._translation_fields:
                        for y in m.objects.all():
                            db_values.append( getattr(y, x) )

        #print db_values
        f = file('db_translation.html', "w")
        """ blocktrans and we dont have to worry about to escape the string etc."""   
        for v in db_values:            
            f.write('{%% blocktrans %%}%s{%% endblocktrans %%}\n' % smart_str(v))
        f.close()
