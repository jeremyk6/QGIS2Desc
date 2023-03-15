from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterMatrix
from qgis.core import QgsProcessingParameterFeatureSink
import processing

from processing.gui.wrappers import WidgetWrapper
from qgis.gui import QgsCodeEditorPython

import json

class CodeEditor(WidgetWrapper):

    def createWidget(self):
        self._combo = QgsCodeEditorPython()
        return self._combo

    def value(self):
        return self._combo.text()

    def setValue(self, value):
        self._combo.setText(value)

def tr(message):
    return QCoreApplication.translate('DescTools', message)

class Creator(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('layer', 'Couche initiale', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        param = QgsProcessingParameterString('desc_function', 'Fonction de description', multiLine=True, defaultValue='from pyrealb import *\n\n# f is a dictionary with layer\'s attributes names as keys.\n# Each attribute can be accessed like this : f["name"]\ndef description(f):\n  return("")')
        param.setMetadata({'widget_wrapper': {'class': CodeEditor}})
        self.addParameter(param)
        self.addParameter(QgsProcessingParameterMatrix('metadata', 'Métadonnées', numberRows=1, hasFixedNumberRows=False, headers=['Paramètre','Valeur'], defaultValue=['type','0','order','0','style','text']))
        self.addParameter(QgsProcessingParameterFeatureSink('output_layer', 'Nouvelle couche', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}
        
        # Ajout du champ description
        alg_params = {
            'FIELD_LENGTH': 9999,
            'FIELD_NAME': 'description',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,  # Texte (chaîne de caractères)
            'FORMULA': 'value = description({%s})'%(','.join(["'%s' : <%s>"%(field, field) for field in [field.name() for field in self.parameterAsLayer(parameters, "layer", context).fields()]])),
            'GLOBAL': parameters['desc_function'],
            'INPUT': parameters['layer'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        layer_description = processing.run('qgis:advancedpythonfieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Ajout du champ metadata
        metadata = {}
        for i in range(0, len(parameters['metadata']), 2):
            metadata[parameters['metadata'][i]] = parameters['metadata'][i+1]
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'metadata',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Texte (chaîne de caractères)
            'FORMULA': "'%s'"%json.dumps(metadata),
            'INPUT': layer_description,
            'OUTPUT': parameters['output_layer']
        }
        results['output_layer'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        return results

    def name(self):
        return 'Concevoir une description'

    def displayName(self):
        return 'Concevoir une description'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Creator()
