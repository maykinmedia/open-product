from django.forms import Textarea


class WysimarkWidget(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {"class": "wysimark-textarea"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    class Media:
        js = ("wysimark/wysimark.js", "wysimark/textarea-wysimark.js")
        css = {"all": ("css/wysimark-tweaks.css",)}
