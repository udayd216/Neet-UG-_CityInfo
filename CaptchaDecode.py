import cv2
import numpy as np
import typing
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

        # Get model input details
        self.input_name = self.model.get_inputs()[0].name  # Extract input name
        self.input_shape = self.model.get_inputs()[0].shape  # Extract input shape

    def predict(self, image: np.ndarray):
        # Ensure correct width-height order for OpenCV resizing
        image = cv2.resize(image, (self.input_shape[2], self.input_shape[1]))  
        image_pred = np.expand_dims(image, axis=0).astype(np.float32)
        preds = self.model.run(None, {self.input_name: image_pred})[0]  # Use extracted input_name
        text = ctc_decoder(preds, self.char_list)[0]
        return text
