from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterMultipleLayers
from qgis.core import QgsProcessingParameterFileDestination
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsFeatureRequest
import processing

from pyrealb import *
from .libs.crdoc.html import *
import json

def tr(message):
    return QCoreApplication.translate('DescTools', message)

class Assembler(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMultipleLayers('layers', 'Couches décrites', layerType=QgsProcessing.TypeMapLayer, defaultValue=None))
        self.addParameter(QgsProcessingParameterString('document_title', 'Titre du document', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterString('description_type', 'Type de description', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterFileDestination('description', 'Description', optional=False, fileFilter='Tous les fichiers (*.*)', createByDefault=False, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        description_type = parameters['description_type']

        root = DocumentRoot(parameters['document_title'])
        documentSlots = [None for i in range(10)]

        layers = self.parameterAsLayerList(parameters, 'layers', context)
        
        for layer in layers:

            container = Paragraph()
            style = "text"

            metadata = None
            descriptions = []
            for feature in layer.getFeatures():
                descriptions.append(json.loads(feature['description']))
                metadata = json.loads(feature['metadata'])

            # Check if the description type corresponds to what we want, else we don't describe the layer
            if "type" in metadata.keys():
                if metadata["type"] != description_type:
                    continue
            else:
                continue
            
            # Add the title of the layer if any
            if "title" in metadata.keys():
                container.add_child(
                    Title2().add_child(
                        Text(metadata["title"])
                    )
                )

            # Check the style of the layer
            if "style" in metadata.keys():
                style =  metadata['style']

            Elements = List()

            for description in descriptions:

                paragraph = Paragraph()

                # If the description is a list, it contains mulitple sentences to merge
                if isinstance(description, list):
                    paragraph = Paragraph()
                    for sentence in description:
                        sentence = fromJSON(sentence)
                        paragraph.add_child(
                            Text(sentence)
                        )
                else:
                    description = fromJSON(description)
                    paragraph.add_child(
                            Text(description.realize())
                    )
                
                if style == "list":
                    Elements.add_child(
                        ListElement().add_child(
                            paragraph
                        )
                    )
                else:
                    container.add_child(paragraph)
            
            if style=="list":
                container.add_child(Elements)

            # Put the container in the right slot
            order = 0
            if "order" in metadata.keys():
                order = int(metadata["order"])
            documentSlots[order] = container

        # Add each container to the document root
        for container in documentSlots:
            if container is not None:
                root.add_child(container)

        file = open(self.parameterAsFileOutput(parameters, 'description', context), "w")
        file.write(root.toString())
        file.close()

        results['description'] = self.parameterAsFileOutput(parameters, 'description', context)

        return results

    def name(self):
        return 'Assembler des descriptions'

    def displayName(self):
        return 'Assembler des descriptions'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Assembler()
