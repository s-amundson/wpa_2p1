import io
import base64
from django import forms
from pyzbar.pyzbar import decode, ZBarSymbol
from PIL import Image
from django_ckeditor_5.widgets import CKEditor5Widget
from ..models import Bow, BowInventory
import logging
logger = logging.getLogger(__name__)

class BowForm(forms.ModelForm):
    class Meta:
        model = Bow
        fields = ['bow_id', 'hand', 'poundage', 'length', 'type', 'riser_material', 'riser_manufacturer',
                  'riser_color', 'limb_color', 'limb_manufacturer', 'limb_model', 'in_service','is_youth', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['bow_id'].widget.attrs.update({'readonly': 'readonly'})
        else:
            self.fields["bow_id"].required = False
            self.fields["bow_id"].widget = forms.HiddenInput()
        self.fields['is_youth'].required = False
        self.fields['in_service'].required = False

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(cleaned_data['bow_id'])
        if cleaned_data['bow_id'] == "":
            next_id = self.Meta.model.objects.next_id(self.cleaned_data['hand'], self.cleaned_data['poundage'])
            cleaned_data['bow_id'] = f"{self.cleaned_data['hand']}{self.cleaned_data['poundage']}{next_id:02d}"
        logger.debug(cleaned_data['bow_id'])
        return cleaned_data

class BowInventoryForm(forms.ModelForm):
    class Meta:
        model = BowInventory
        fields = ['bow', 'user']
        widgets = {
            'bow': forms.HiddenInput(),
            'user': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bow_id'] = forms.CharField(required=False)
        self.fields["image_field"] = forms.ImageField(required=False)
        self.fields['image'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        self.fields['bow'].required = False


    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['bow_id'] == "":
            if cleaned_data['image_field']:
                image = Image.open(cleaned_data['image_field'])
            else:
                image_b64 = cleaned_data.pop('image')
                img_format, imgstr = image_b64.split(';base64,')
                try:
                    data = base64.b64decode(imgstr)
                    buf = io.BytesIO(data)
                    image = Image.open(buf)
                except:
                    # self.add_error(None, "captured image error")
                    logger.debug('error')
                    raise forms.ValidationError("captured image error")
            # image = Image.open(cleaned_data['image'])
            image = image.convert("L")
            image.save('bcode1.jpg')
            dcode = decode(image) #, ZBarSymbol.CODE128)
            logger.debug(dcode)
            if len(dcode):
                cleaned_data['bow_id'] = dcode[0].data.decode()
            else:
                self.raise_error(cleaned_data, 'could not read barcode from captured image')
        cleaned_data['bow'] = Bow.objects.filter(bow_id=cleaned_data['bow_id']).first()
        if cleaned_data['bow'] is None and not len(self.errors.items()):
            self.raise_error(cleaned_data, 'Bow not found')
        return cleaned_data

    #
    def raise_error(self, cleaned_data, message):
        if cleaned_data['image_field']:
            self.add_error('image_field', message)
        else:
            self.add_error('image', message)
        # raise forms.ValidationError(message)