from django.core.management import BaseCommand, CommandError
from django.db import models
from django.utils.encoding import smart_str

class Command(BaseCommand):
    help = "Translate database messages"

    requires_model_validation = False

    def handle(self, *args, **options):
        db_values = []
        """ Taken from django.core.management.comanns.syncdb"""
        for app in models.get_apps():
            #obsolete for us
            #app_name = app.__name__.split('.')[-2]
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
