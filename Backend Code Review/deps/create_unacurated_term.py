from catalyst_api_utils.logger import logger
from trialsai.statements.ontology_class import OntologyClass
from ...common_constants import common_constants as common_constants
from slugify import slugify


class CreateUncuratedTerm:
    """
    Purpose: Class to create uncurated term
    """

    def create(self, label):
        """
        Purpose: Function to create uncurated term
        """
        
        logger.info(f"Create uncurated term type")

        new_ontclass = []
        
        logger.info("New ontclass from dict for ")
        

        slug = slugify(label.get(common_constants.LABEL_KEY))
        # do a sanity check here by seeing if we already have an ontology class
        # for this slug
        existing = OntologyClass().query(
            filter={common_constants.SLUG_KEY: {common_constants.EQ_KEY: slug}},
            first=True,
        )
        if existing:
            logger.info(f"Existing uncurated term for this slug {slug}")
            new_ontclass.append(existing.to_dict())
            return new_ontclass

        # ontclass will be a subClassOf this
        uncurated_term_class = OntologyClass().query(
            filter={
                common_constants.SLUG_KEY: {
                    common_constants.EQ_KEY: common_constants.UNCURATED_TERM_KEY
                }
            },
            first=True,
        )

        # create it
       
        ontclass = OntologyClass().from_dict(label)
        ontclass.add_subClassOf(uncurated_term_class)
        ontclass.save()
        new_ontclass.append(OntologyClass().get(uuid=ontclass.uuid).to_dict())

        logger.info("Created new uncurated terms:")
        logger.info(new_ontclass)
        return new_ontclass