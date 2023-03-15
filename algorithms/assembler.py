from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback,\
    QgsProcessingParameterVectorLayer, QgsProcessingParameterField, QgsProcessingParameterString,\
    QgsProcessingParameterMultipleLayers, QgsProcessingParameterFileDestination, QgsProcessingParameterFeatureSink,\
    QgsFeatureRequest, QgsProcessingParameterMatrix
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
        self.addParameter(QgsProcessingParameterMatrix('metadata_filter', 'Sélection par métadonnées', numberRows=1, hasFixedNumberRows=False, headers=['Paramètre','Valeur'], defaultValue=['type','0']))
        self.addParameter(QgsProcessingParameterMatrix('assembly', 'Assemblage du document', numberRows=1, hasFixedNumberRows=False, headers=['Nom','Titre','Style']))
        self.addParameter(QgsProcessingParameterFileDestination('description', 'Description', optional=False, fileFilter='Tous les fichiers (*.*)', createByDefault=False, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        metadata_filter = {}
        for i in range(0, len(parameters['metadata_filter']), 2):
            metadata_filter[parameters['metadata_filter'][i]] = parameters['metadata_filter'][i+1]
        
        assembly = []
        for i in range(0, len(parameters['assembly']), 3):
            assembly.append({"name": parameters['assembly'][i], "title": parameters['assembly'][i+1], "style": parameters['assembly'][i+2]})

        layers = self.parameterAsLayerList(parameters, 'layers', context)

        root = DocumentRoot(parameters['document_title'])
        documentSlots = []

        for element in assembly:
            layer = None
            metadata = None
            for layer in layers:

                # Get layer metadatas
                for feature in layer.getFeatures():
                    metadata = json.loads(feature['metadata'])
                    break
                
                # Compare metadatas
                if element["name"] == metadata["name"]:
                    pass_filter = True
                    for key in metadata_filter.keys():
                        if (key in metadata and metadata[key] == metadata_filter[key]) == false:
                            pass_filter = false
                            break
                    if pass_filter: break

                layer = None

            if(layer):
                container = Paragraph()
                descriptions = [json.loads(feature['description']) for feature in layer.getFeatures()]
                
                # Add the title of the layer if any
                if element["title"]:
                    container.add_child(
                        Title2().add_child(
                            Text(element["title"])
                        )
                    )

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
                    
                    if element["style"] == "list":
                        Elements.add_child(
                            ListElement().add_child(
                                paragraph
                            )
                        )
                    else:
                        container.add_child(paragraph)
                
                if element["style"]=="list":
                    container.add_child(Elements)

                documentSlots.append(container)

        # Add each container to the document root
        for container in documentSlots:
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
