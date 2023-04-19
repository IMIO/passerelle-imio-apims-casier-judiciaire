from django.db import models
from django.http import HttpResponse
from django.urls import reverse
from django.core.exceptions import ValidationError
from passerelle.base.models import BaseResource
from passerelle.utils.api import endpoint
from passerelle.utils.jsonresponse import APIError
import requests
from requests import RequestException
import base64

def validate_url(value):
    if value.endswith("/"):
        raise ValidationError(
            '%(value)s ne dois pas finir avec un "/"',
            params={'value': value},
        )

class ApimsCasierJudiciaireConnector(BaseResource):
    """
    Connecteur APIMS Casier Judiciaire
    Attributes
    ----------
    url : str
        url used to connect to APIMS
    username : str
        username used to connect to APIMS
    password : str
        password used to connect to APIMS
    municipality_nis_code : str
        token used to identify municipality to APIMS 
    Methods
    -------
    """
    url = models.URLField(
        max_length=128,
        blank=True,
        verbose_name="URL",
        help_text="URL de APIMS Casier Judiciaire",
        validators=[validate_url],
        default="https://api-staging.imio.be/bosa/v1"
    )
    username = models.CharField(
        max_length=128,
        blank=True,
        help_text="Utilisateur APIMS Casier Judiciaire",
        verbose_name="Utilisateur",
    )
    password = models.CharField(
        max_length=128,
        blank=True,
        help_text="Mot de passe APIMS Casier Judiciaire",
        verbose_name="Mot de passe",
    )
    municipality_nis_code = models.CharField(
        max_length=128,
        blank=True,
        help_text="Code NIS d'identification de l'organisme dans APIMS Casier Judiciaire",
        verbose_name="Code NIS de l'organisme",
    )
    
    category = 'Connecteurs iMio'

    api_description = "Connecteur permettant d'intéragir avec APIMS Casier Judiciaire"

    class Meta:
        verbose_name = 'Connecteur APIMS Casier Judiciaire'
    
    @property
    def session(self):
        session = requests.Session()
        session.auth = (self.username, self.password)
        session.headers.update({
            "Accept": "application/json",
            "X-IMIO-MUNICIPALITY-NIS": self.municipality_nis_code
        })
        return session


    @endpoint(
        name="list-extract-types",
        perm="can_access",
        description="Types d'extraits de casier judiciaire",
        long_description="Lister les différents types d'extraits de casier judiciaire",
        serializer_type="json-api",
        display_order=0,
        parameters={
            "language": {
                "description": "Langage voulu",
                "example_value": "fr",
            },
        },
        display_category="Types",
    )
    def list_person_documents(self, request, language="fr"):
        """ Gets types of extracts
        Returns
        -------
        dict
            all types with reference
        """
        url = f"{self.url}/cjcs-extract-types"

        self.logger.info("Liste des extraits")
        try:
            response = self.session.get(url, params={"language": language})
        except RequestException as e:
            self.logger.warning(f'Casier Judiciaire APIMS Error: {e}')
            raise APIError(f'Casier Judiciaire APIMS Error: {e}')

        json_response = None
        try:
            json_response = response.json()
        except ValueError:
            self.logger.warning('Casier Judiciaire APIMS Error: bad JSON response')
            raise APIError('Casier Judiciaire APIMS Error: bad JSON response')

        try:
            response.raise_for_status()
        except RequestException as e:
            self.logger.warning(f'Casier Judiciaire APIMS Error: {e} {json_response}')
            raise APIError(f'Casier Judiciaire APIMS Error: {e} {json_response}')
        return json_response
    
    @endpoint(
        name="read-extract",
        perm="can_access",
        methods=["get"],
        description="Lire le casier judiciaire d'une personne",
        parameters={
            "extract_code": {
                "description": "ID du type d'extrait de casier judiciaire",
                "example_value": "595",
            },
            "person_nrn": {
                "description": "Numéro de registre national de la personne qui est concernée par l'extrait de casier judiciaire",
                "example_value": "15010123487",
            },
            "requestor_nrn": {
                "description": "Numéro de registre national de la personne qui demande l'extrait de casier judiciaire",
                "example_value": "15010123487",
            },
            "language": {
                "description": "Langage de l'extrait de casier judiciaire",
                "example_value": "fr",
            },
        },
        display_order=1,
        display_category="Documents"
    )
    def read_extract(self, request, extract_code, person_nrn, requestor_nrn, language="fr"):
        """ Get asked document as PDF
        Parameters
        ----------
        extract_code : str
            Extract's code
        person_nrn : str
            National number for the extract person
        requestor_nrn : str
            National number of the requester
        language : str
            Language of the document
        Returns
        -------
        PDF document
        """

        url = f"{self.url}/cjcs-extracts/{person_nrn}/{extract_code}"

        self.logger.info("Récupération de l'extrait PDF")
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password), 
                headers={
                    "X-IMIO-REQUESTOR-NRN": requestor_nrn,
                    "X-IMIO-MUNICIPALITY-NIS": self.municipality_nis_code
                },
                params={"language": language}
            )
        except Exception as e:
            self.logger.warning(f'Casier Judiciaire APIMS Error: {e}')
            raise APIError(f'Casier Judiciaire APIMS Error: {e}')

        pdf_response = None
        try:
            pdf = base64.b64decode(response.json()["file_content"]) 
            pdf_response = HttpResponse(pdf, content_type="application/pdf")
        except ValueError:
            self.logger.warning('Casier Judiciaire APIMS Error: bad PDF response')
            raise APIError('Casier Judiciaire APIMS Error: bad PDF response')

        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.warning(f'Casier Judiciaire APIMS Error: {e}')
            raise APIError(f'Casier Judiciaire APIMS Error: {e}')
        return pdf_response
    
    @endpoint(
        name="read-extract-demo",
        perm="can_access",
        methods=["get"],
        description="DEMO - Lire le casier judiciaire d'une personne",
        parameters={
            "extract_code": {
                "description": "ID du type d'extrait de casier judiciaire",
                "example_value": "595",
            },
            "person_nrn": {
                "description": "Numéro de registre national de la personne qui est concernée par l'extrait de casier judiciaire",
                "example_value": "15010123487",
            },
            "requestor_nrn": {
                "description": "Numéro de registre national de la personne qui demande l'extrait de casier judiciaire",
                "example_value": "15010123487",
            },
            "language": {
                "description": "Langage de l'extrait de casier judiciaire",
                "example_value": "fr",
            },
        },
        display_order=1,
        display_category="Demo"
    )
    def read_extract_demo(self, request, extract_code, person_nrn, requestor_nrn, commune_nis, language="fr"):
        """ Get asked document as PDF
        Parameters
        ----------
        extract_code : str
            Extract's code
        person_nrn : str
            National number for the extract person
        requestor_nrn : str
            National number of the requester
        commune_nis : str
            Commune's code nis
        language : str
            Language of the document
        Returns
        -------
        PDF document
        """

        url = f"{self.url}/cjcs-extracts/{person_nrn}/{extract_code}"

        self.logger.info("Récupération de l'extrait PDF")
        try:
            response = requests.get(
                url,
                auth=(self.username, self.password), 
                headers={
                    "X-IMIO-REQUESTOR-NRN": requestor_nrn,
                    "X-IMIO-MUNICIPALITY-NIS": commune_nis
                },
                params={"language": language}
            )
        except Exception as e:
            self.logger.warning(f'Casier Judiciaire APIMS Error: {e}')
            raise APIError(f'Casier Judiciaire APIMS Error: {e}')

        pdf_response = None
        try:
            pdf = base64.b64decode(response.json()["file_content"]) 
            pdf_response = HttpResponse(pdf, content_type="application/pdf")
        except ValueError:
            self.logger.warning('Casier Judiciaire APIMS Error: bad PDF response')
            raise APIError('Casier Judiciaire APIMS Error: bad PDF response')

        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.warning(f'Casier Judiciaire APIMS Error: {e}')
            raise APIError(f'Casier Judiciaire APIMS Error: {e}')
        return pdf_response

