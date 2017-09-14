import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Found at http://djangosnippets.org/snippets/976/

        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):

        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        # If the filename already exists,
        # remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


def save_to_logo(instance, filename):
    # return "".join(["data/logos/", str(instance.id), "/", filename])
    return "logo-{0}-{1}".format(instance.challenge.id, filename)


def save_to_baseline(instance, filename):
    # return "".join(["data/baseline/", str(instance.id), "/", filename])
    return "baseline-{0}-{1}".format(instance.challenge.id, filename)


def save_to_bundle(instance, filename):
    # return "".join(["data/bundles/", str(instance.challenge.id), "/", filename])
    return "bundle-{0}-{1}".format(instance.challenge.id, filename)
