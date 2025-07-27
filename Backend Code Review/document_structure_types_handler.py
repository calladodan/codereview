from django.conf import settings
from catalyst_api_utils.logger import logger
from rest_framework import viewsets
from trialsai.statements.document_structure import DocumentStructure
from trialsai.statements.ontology_class import OntologyClass
from ..common_constants import common_constants as common_constants
from ..handlers.uncurated_term_handler import UncuratedTermHandler
from ..models.uncurated_term.create_unacurated_term import CreateUncuratedTerm

class DocumentStructureTypesViewSetHandler():
    """
    Purpose: Class for handling the creation of document structure types
    graphql mutation: createDocumentStructureType()
    required: parent: string // slug
    required: doctype {uuid}
    required: ontology_class {uuid}
    required: relationship string
    """

    def create(self, request):
        """
        Purpose: Function for creating document structure types view set
        Input : request object
        Output : Response dictionary containing New docstructure objects created and status
        as "success" for success, error message and status as "failed" for failure
        """
        try:
            response = {}
            unacurated_obj = CreateUncuratedTerm()
            logger.info("Creating document structure type")
            logger.info("lable: %s", request.data[common_constants.DATA_KEY])
            
            # validate before creating anything
            for ds in request.data[common_constants.DATA_KEY]:
                # all docstructs must have a doctype
                if (
                    common_constants.DOCTYPE_KEY not in ds
                    or common_constants.UUID_KEY not in ds[common_constants.DOCTYPE_KEY]
                    or not ds[common_constants.DOCTYPE_KEY][common_constants.UUID_KEY]
                ):
                    raise Exception("All docstructs must have a doctype uuid")

                # must have a parent since this is a docstruct type
                
                # must have an ontology class
                
            new_docstructs = []
            for ds in request.data[common_constants.DATA_KEY]:
                logger.info("New docstruct from dict for ")
                logger.info(ds)
            
                # get the ontology class
               
                if common_constants.ONTOLOGY_CLASS_KEY in ds:
                    
                    ont_class = OntologyClass().get(
                        uuid=ds[common_constants.ONTOLOGY_CLASS_KEY][
                            common_constants.UUID_KEY
                        ]
                    )
                    if not ont_class or not ont_class.uuid:
                        raise Exception("Invalid ontology_class provided")

                # get docstruct types should always have a docstruct
                # for which they are a type: a.k.a. parent
                if common_constants.PARENT_KEY in ds:
                    parent_uuid = ds[common_constants.PARENT_KEY]
                    parent = DocumentStructure().get(uuid=parent_uuid)
                # make sure parent is valid
                    if not parent or not parent.uuid:
                        raise Exception(
                            "Parent for docstruct type not found for uuid: %s",
                            str(parent_uuid),
                        )

                    # docstruct.slug should always be the same as ontology_class.slug
                    # do a sanity check here by seeing if we already have a docstruct
                    # for this ontology_class.slug
                    existing = DocumentStructure().query(
                        filter={
                            common_constants.SLUG_KEY: {
                                common_constants.EQ_KEY: ont_class.slug
                            }
                        }
                    )
                    if existing:
                        logger.info(
                            "Existing document structure for this ontology class: %s",
                            ont_class.slug,
                    )
                    # if you are trying to set this as a type
                    # update the parent instead
                    new_docstructs.append(existing[0].to_dict())
                    continue
                if common_constants.PARENT_KEY in ds:
                    del ds[common_constants.PARENT_KEY]
                    ds[common_constants.SLUG_KEY] = ont_class.slug
                    logger.info(f"Created docstruct successfully from data: {ds}")
                    docstruct = DocumentStructure().from_dict(ds)
                    docstruct.save()
                    new_docstructs.append(
                        DocumentStructure().get(uuid=docstruct.uuid).to_dict()
                    )

                    # add this as a type for the parent
                    logger.info(
                        "Adding docstruct %s as type for parent %s",
                        str(docstruct.uuid),
                        str(parent.uuid),
                    )
                    parent.add_docstruct_type(docstruct_type=docstruct)
                    parent.save()
                
                
                # ****************optmize new  code************
                if common_constants.NEW_ONTOLOGY_CLASS_KEY in ds:
                
                
                    label={
                            "label": ds[common_constants.NEW_ONTOLOGY_CLASS_KEY]
                        }
                    
                    ont_class =unacurated_obj.create(label)
    
                    if not ont_class :
                        raise Exception("Invalid ontology_class provided")
            
                # get docstruct types should always have a docstruct
                # for which they are a type: a.k.a. parent
                if common_constants.PARENT_SLUG_KEY in ds:
                    docstruct = DocumentStructure().from_dict(ds)
                    parent_slug = ds[common_constants.PARENT_SLUG_KEY]
                
                    if not parent_slug :
                        raise Exception(
                            "Parent for docstruct type not found for parent slug: %s"
                        )

                    slug=  ont_class[0]['slug']
                    
                    existing = DocumentStructure().query(
                        filter={
                            common_constants.SLUG_KEY: {
                                common_constants.EQ_KEY: slug
                            }
                        }
                    )
                    if existing:
                        logger.info(
                            "Existing document structure for this ontology class: %s",
                            slug,
                    )
                    # if you are trying to set this as a type
                    # update the parent instead
                    new_docstructs.append(existing[0].to_dict())
                    continue
                if common_constants.PARENT_SLUG_KEY in ds:
                    del ds[common_constants.PARENT_SLUG_KEY]
                    ds[common_constants.SLUG_KEY] = slug
                    logger.info(f"Created docstruct successfully from data: {ds}")
                    docstruct = DocumentStructure().from_dict(ds)
                    docstruct.save()
                    new_docstructs.append(
                        DocumentStructure().get(uuid=docstruct.uuid).to_dict()
                    )

                    # add this as a type for the parent
                    logger.info(
                        "Adding docstruct %s as type for parent %s",
                        str(docstruct.uuid)
                        
                    )
                    parent.add_docstruct_type(docstruct_type=docstruct)
                    parent.save()
                
            logger.info("Created new document structures:")
            logger.info(new_docstructs)
            response[common_constants.STATUS_KEY] = common_constants.SUCCESS_KEY
            response[common_constants.RESULT_KEY] = new_docstructs
            return response
        
        except Exception as exception:
            logger.error("Error in %s : %s", self.create.__name__, exception)
            response[common_constants.STATUS_KEY] = common_constants.FAILED_KEY
            response[common_constants.ERROR_KEY] = exception
            return response

    # maps to deleteDocumentStructureByUuid
    def destroy(self, request, pk):
        """
        Purpose: Function to destroy a docstruct using uuid
        Input : Request object, primary key(pk or uuid of docstruct)
        Ouput : Response dictionary containing -Docstruct deleted and response status as
        "success" in case of "success"
        Error message and status as "failed" in case of failure
        """
        response = {}
        try:
            logger.info("Called delete docstruct by uuid: %s", {pk})
            # delete docstruct:
            # delete all renderings
            # should automatically be removed from sections, categories and groups
            # get the docstruct obj and delete it
            docstruct = DocumentStructure().get(uuid=pk)
            deletedDocStruct = docstruct.delete()
            logger.info("Result from delete statement %s", str(deletedDocStruct))
            response[common_constants.STATUS_KEY] = common_constants.SUCCESS_KEY
            response[common_constants.RESULT_KEY] = deletedDocStruct
            return response
        except Exception as exception:
            logger.error("Error in %s : %s", self.destroy.__name__, exception)
            response[common_constants.STATUS_KEY] = common_constants.FAILED_KEY
            response[common_constants.ERROR_KEY] = exception
            return response
