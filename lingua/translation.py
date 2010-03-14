from django.db.models import signals
import handler

signals.post_init.connect(handler.post_init)

class Translation(object):

    def contribute_to_class(self, main_cls, name):
        """Get translation fields and convert them then the class is ready
           Django set the model fields as attributes 
        """        
        import settings
        if hasattr(settings, 'LANGUAGES'):
            _languages = dict(settings.LANGUAGES)
        else:
            _languages = {}

        translation_fields = []
        for x in [x for x in self.__dict__ if '__' not in x]:
            x = x.lower()
            translation_fields.append(x)
            main_cls.add_to_class(x, self.__dict__[x])
        
        main_cls.add_to_class('_translation_fields', tuple(translation_fields))
        main_cls.add_to_class('_languages', _languages)     
        
    contribute_to_class = classmethod(contribute_to_class)
